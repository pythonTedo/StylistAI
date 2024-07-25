# StylistAI

## Backend API Documentation

### Overview

This project is a backend application built using Flask, designed to provide a chatbot service with text generation, image recommendation and clothing generation features. The application leverages OpenAI's GPT for conversation handling, [Thenewblack](https://thenewblack.ai/) applicaiton for outfit generation and a pre-trained TensorFlow model for image feature extraction

### Technologies Used

- **Flask**: Web framework for Python.
- **Flask-SQLAlchemy**: ORM for database interactions.
- **TensorFlow**: Machine learning library used for image processing.
- **OpenAI GPT-3.5-turbo**: Used for natural language processing and generating responses.
- **Pillow**: Python Imaging Library for image processing.
- **Requests**: For making HTTP requests to external APIs.

### Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pythonTedo/StylistAI.git
   cd StylistAI
   ```

2. **Install dependencies**:
   Make sure you have Python 3.10. Install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Pull large files**:
    Make sure to install Git LFS
    ```bash
    sudo apt-get install git-lfs

    git lfs install

    git lfs pull
    ```

4. **Environment Variables**:
   Create a `.env` file in the app directory and add the following environment variables:
   ```
   SECRET_KEY=your_secret_key
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://username:password@localhost/database
   OPENAI_API_KEY=your_openai_api_key
   EMAIL=your_email
   PASSWORD=your_password
   ```

5. **Database Setup**:
   Ensure that MySQL is running and the database specified in `SQLALCHEMY_DATABASE_URI` is created. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. **Run the Application**:
   ```bash
   python app.py
   ```

7. **IMPORTANT for Recommendation System**:

    #### The recommendation system uses images which are stored locally! So if you want to test the recommendation system it will give error of not finding the images. The folder itself is > 20GB large.

### Key Features

1. **User Authentication**:
   - Register and login functionality using sessions.

2. **Chatbot**:
   - Integrates with OpenAI GPT-3.5-turbo to handle user conversations.
   - Stores user and bot messages in a MySQL database.

3. **Image Recommendation**:
   - Users can upload images to receive similar image recommendations.
   - Uses a pre-trained TensorFlow model to extract features from images and find similar items based on cosine similarity.

4. **Clothing Generation**:
   - Sends descriptions to an external API to generate clothing recommendations.

### API Endpoints

- **GET /**:
  - Renders the homepage.

- **GET /chat**:
  - Renders the chat page. Requires user to be logged in.

- **GET, POST /login**:
  - Handles user login.

- **GET, POST /register**:
  - Handles user registration.

- **GET /logout**:
  - Logs out the user.

- **POST /send_message**:
  - Handles sending messages from the user and getting responses from the bot or generating recommendations.

#### For further information look at the [POSTMAN DOC](./POSTMAN.md)

### Project Structure
- **app**: The webserver folder
    - **app.py**: Main application file.
    - **static/**: Contains static files (CSS, JS, images).
    - **templates/**: HTML templates for rendering pages.
- **large_files/ml**: Contains all the wights and vectors for the recommendation system
- **createDB.sql**: Consist of script creating manually the Database tables
- **recommender_sys.ipynb**: Is the notebook where all the training of the recommender system took place

### Contribution

Feel free to fork the project and submit pull requests. For major changes, please open an issue to discuss what you would like to change.

### License

This project is licensed under the MIT License.

---

This README provides a basic guide to setting up and using the backend service. Make sure to configure your environment variables and dependencies properly. For any issues or contributions, please refer to the project repository on GitHub.