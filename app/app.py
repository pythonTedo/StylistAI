import datetime
from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import base64
import tensorflow as tf
from dotenv import load_dotenv
import openai
from openai import OpenAI
import requests
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from tensorflow.keras.applications.xception import preprocess_input
import matplotlib.pyplot as plt
import pickle
import io
from sqlalchemy.dialects.mysql import LONGTEXT

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456Test@localhost/chatbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Set the OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
API_CLOATHING_URL = 'https://thenewblack.ai/api/1.1/wf/clothing'
FEATURE_EXTRACTOR_MODEL = tf.keras.models.load_model('..\\large_files\\ml\\feature_extractor_model.keras')
ALL_FEATURES_PCA = np.load('..\\large_files\\ml\\all_features_pca.npy')
with open('..\\large_files\\ml\\pca_model.pkl', 'rb') as f:
    PCA_MODEL = pickle.load(f)
with open('..\\large_files\\ml\\train_files.pkl', 'rb') as f:
    TRAIN_FILES = pickle.load(f)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=True)
    image_base64 = db.Column(LONGTEXT, nullable=True)  # Store as Text to directly store the base64 string
    is_bot = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_conversation_history(user_id, limit=4):
    """
    Fetches the last `limit` messages between the user and the bot.
    :param user_id: The ID of the user.
    :param limit: The number of messages to fetch.
    :return: A list of messages formatted for the OpenAI API.
    """
    messages = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).limit(limit).all()
    messages.reverse()  # To get them in the order they were sent

    conversation_history = []
    for msg in messages:
        role = "assistant" if msg.is_bot else "user"
        conversation_history.append({
            "role": role,
            "content": msg.text
        })

    return conversation_history


def get_model_response(messages):
    """
    Calls the OpenAI API to get a response from the model.
    :param messages: The conversation history.
    :return: The response from the model.
    """
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )

    return chat_completion.choices[0].message.content

def save_bot_message(user_id, text, image_base64=None):
    """
    Saves the bot's response to the database.
    :param user_id: The ID of the user.
    :param text: The response text.
    :param image_base64: The base64-encoded image.
    :param is_bot: Whether the message is from the bot.
    """
    bot_message = Message(user_id=user_id, text=text, image_base64=image_base64, is_bot=True)
    db.session.add(bot_message)
    db.session.commit()
    return bot_message

def save_user_response(user_id, text, image_base64):
    """
    Saves the user's response to the database.
    :param user_id: The ID of the user.
    :param text: The text of the user's message.
    :param image_base64: The base64-encoded image.
    """
    new_message = Message(user_id=user_id, text=text, image_base64=image_base64, is_bot=False)
    db.session.add(new_message)
    db.session.commit()


def send_cloathing_gen(outfit, email=EMAIL, password=PASSWORD, gender="man", country="Germany", negative="ugly face, ugly hands", api_url=API_CLOATHING_URL):
    """
    Sends a request to the Cloathing API to generate an outfit.
    :param email: The email of the user.
    :param password: The password of the user.
    :param outfit: The outfit description.

    :return: The response from the API.
    """
    form_data = {
            'email': email,
            'password': password,
            'outfit': outfit,
            'gender': gender,
            'country': country,
            'negative': negative
        }
        
        # Make the API call
    response = requests.post(api_url, data=form_data)
        
        # Check the content type of the response
    if response.headers.get('Content-Type') == 'application/json':
        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text
    else:
        response_data = response.text
    return response_data

def compute_recommendations(image):
    """
    Calls the OpenAI API to get a response from the model.
    :param image: The image to process.
    :return: The response from the model.
    """
    def load_and_preprocess_image(image_path, target_size):
        try:
            img = Image.open(image_path)
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height

            if aspect_ratio > 1:
                new_width = target_size[0]
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = target_size[1]
                new_width = int(new_height * aspect_ratio)

            img = img.resize((new_width, new_height), Image.LANCZOS)
            new_img = Image.new("RGB", target_size, (255, 255, 255))
            new_img.paste(img, ((target_size[0] - new_width) // 2, (target_size[1] - new_height) // 2))

            return new_img
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None

    def get_image_features(image_path, model, pca):
        preprocessed_image = load_and_preprocess_image(image_path, (299, 299))
        if preprocessed_image is None:
            return None
        img_array = img_to_array(preprocessed_image)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        features = model.predict(img_array)
        features_pca = pca.transform(features)
        return features_pca

    def find_similar_images_for_unseen(image_path, feat_extractor, pca, all_features_pca, train_files, top_n=5):
        image_features_pca = get_image_features(image_path, feat_extractor, pca)
        if image_features_pca is None:
            print("Error processing the input image.")
            return None

        # Calculate similarities
        cosine_similarities = cosine_similarity(image_features_pca, all_features_pca)[0]
        euclidean_similarities = -euclidean_distances(image_features_pca, all_features_pca)[0]

        # Get top N similar images
        top_indices_cosine = np.argsort(cosine_similarities)[::-1][:top_n]
        top_indices_euclidean = np.argsort(euclidean_similarities)[::-1][:top_n]

        # Ensure paths are correctly constructed
        base_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fashion-dataset', 'fashion-dataset', 'images')
        top_similarities_cosine = [(os.path.join(base_image_path, os.path.basename(train_files[idx])), float(cosine_similarities[idx])) for idx in top_indices_cosine]
        top_similarities_euclidean = [(os.path.join(base_image_path, os.path.basename(train_files[idx])), float(euclidean_similarities[idx])) for idx in top_indices_euclidean]

        return top_similarities_cosine, top_similarities_euclidean

    # Save the image temporarily and get the file path
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_image_path = os.path.join(temp_dir, "temp_image.jpg")
    image.save(temp_image_path)

    top_similarities_cosine, top_similarities_euclidean = find_similar_images_for_unseen(
        temp_image_path, FEATURE_EXTRACTOR_MODEL, PCA_MODEL, ALL_FEATURES_PCA, TRAIN_FILES, top_n=5
    )

    # Convert input and recommended images to base64
    original_image = Image.open(temp_image_path)
    original_image_base64 = image_to_base64(original_image)

    recommended_images_base64 = []
    for img_path, score in top_similarities_cosine:
        normalized_img_path = os.path.normpath(img_path)
        if os.path.exists(normalized_img_path):
            try:
                img = Image.open(normalized_img_path)
                img_base64 = image_to_base64(img)
                recommended_images_base64.append({"image": img_base64, "score": score})
            except Exception as e:
                print(f"Error opening image {normalized_img_path}: {e}")
        else:
            print(f"Image does not exist: {normalized_img_path}")

    return original_image_base64, recommended_images_base64

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/chat")
def chat():
    if 'user_id' not in session:
        flash("You need to login first", "danger")
        return redirect(url_for("login"))
    
    user = User.query.filter_by(id=session['user_id']).first()
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("login"))

    messages = [message for message in Message.query.filter_by(user_id=user.id).all()]
    for message in messages:
        message.text = message.text.strip() if message.text else "" # Assuming the message text is stored in 'content'
        
    # No need to re-encode here if stored correctly
    return render_template("chat.html", username=user.username, messages=messages)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("chat"))
        else:
            flash("Invalid credentials", "danger")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash("Registration successful!", "success")
        return redirect(url_for("chat"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))

@app.route("/send_message", methods=["POST"])
def send_message():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"})

    text = request.form.get("msg")
    image = request.files.get("image")
    generate = request.form.get("generate", "0")
    image_base64 = None

    if text is None:
        return jsonify({"success": False, "error": "No text provided"})

    if image:
        original_image_base64, recommended_images_base64 = compute_recommendations(image)

        # Convert all scores to float to ensure they are JSON serializable
        bot_message = {
            "text": "Here are your recommendations",
            "timestamp": datetime.datetime.now().strftime('%H:%M'),  # replace with actual timestamp if needed
            "image_base64": original_image_base64,
            "recommended_images": [{"image": rec["image"], "score": float(rec["score"])} for rec in recommended_images_base64]
        }

        save_bot_message(user_id, bot_message["text"], bot_message["image_base64"])
        for rec in bot_message["recommended_images"]:
            save_bot_message(user_id, "", rec["image"])

        return jsonify({
            "success": True, 
            "bot_message": bot_message
        })
    
    save_user_response(user_id, text, image_base64)

    if generate == "1":
        response = send_cloathing_gen(text)
        print(f"Response from API: {response}")
        message = save_bot_message(user_id, response)
        return jsonify({"success": True, "bot_message": {"text": response, "timestamp": message.timestamp.strftime('%H:%M')}})

    # Get the conversation history
    conversation_history = get_conversation_history(user_id, limit=3)
    # Add the current user message
    user_message = {"role": "user", "content": text}
    conversation_history.append(user_message)

    # Extract the response content correctly
    bot_response = get_model_response(conversation_history)

    # Save the bot response to the database
    new_message = save_bot_message(user_id, bot_response)
    
    return jsonify({"success": True, "bot_message": {"text": bot_response, "timestamp": new_message.timestamp.strftime('%H:%M')}})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8081, host='0.0.0.0')
