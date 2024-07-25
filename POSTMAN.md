### Using API Endpoints with Postman

To interact with the backend API using Postman, follow the detailed instructions for each endpoint below. Ensure that the server is running and accessible.

#### 1. **Register a New User**

- **Endpoint**: `POST /register`
- **Description**: Creates a new user account.

**Postman Configuration**:
- **Method**: POST
- **URL**: `http://localhost:8081/register`
- **Body**: Select `x-www-form-urlencoded`
  - `username`: Desired username (e.g., `johndoe`)
  - `password`: Desired password

**Response**:
- **Success**: Redirects to chat page with a success message.
- **Failure**: Returns an error message if the username already exists.

#### 2. **User Login**

- **Endpoint**: `POST /login`
- **Description**: Logs in an existing user.

**Postman Configuration**:
- **Method**: POST
- **URL**: `http://localhost:8081/login`
- **Body**: Select `x-www-form-urlencoded`
  - `username`: Existing username
  - `password`: Password associated with the username

**Response**:
- **Success**: Redirects to chat page with a success message.
- **Failure**: Returns an error message if the credentials are incorrect.

#### 3. **User Logout**

- **Endpoint**: `GET /logout`
- **Description**: Logs out the current user.

**Postman Configuration**:
- **Method**: GET
- **URL**: `http://localhost:8081/logout`

**Response**:
- **Success**: Redirects to login page with a success message.

#### 4. **Send a Message**

- **Endpoint**: `POST /send_message`
- **Description**: Sends a message from the user to the bot. If an image is included, the system provides image recommendations.

**Postman Configuration**:
- **Method**: POST
- **URL**: `http://localhost:8081/send_message`
- **Body**: Select `form-data`
  - `msg`: The message text (optional if `image` is provided)
  - `image`: (Optional) Upload an image file to receive recommendations
  - `generate`: Set to `1` to generate clothing recommendations based on the `msg`

**Use Cases**:
- Chabot functionality: Use only `msg` to send the text and get chatbot seponse
- Outfit generation: Use `msg` and `generate` set to 1 in order to get a link response with the outfit
- Item recommendation: Upload Use `msg` and `image` image file from peace of cloths to get recommended images. 

### Notes

1. **Authentication**: Ensure that you have logged in via the `/login` endpoint before accessing protected endpoints like `/chat` and `/send_message`. The session should be maintained in Postman.

2. **Headers**: If any endpoints require custom headers (e.g., for session management or content type), ensure to set them correctly in Postman.

3. **Error Handling**: Pay attention to the status codes and error messages returned by the API for troubleshooting.

By following these configurations in Postman, you can effectively interact with the backend API for various operations.