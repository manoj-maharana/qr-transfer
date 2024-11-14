# QR Transfer - Flask Application for Seamless File Sharing

## Overview

QR Transfer is a Flask-based web application designed for easy and secure file sharing. The app allows users to generate a QR code, which can be scanned to upload and download files. Users can manage files in an efficient manner with minimal interaction, focusing on a seamless user experience. The app is built with robust security features such as session management, Content Security Policy (CSP) headers, and file cleanup scheduling.

![image](https://github.com/user-attachments/assets/b7f17fbb-9d21-4b87-adf7-4ff34a21c6b3)


## Key Features

- Tool for Quickly Sharing Photos Between Devices via QR Codes
- Generates a Unique QR Code for Each Browser Session
- Mobile-Friendly Upload Page Accessible by Scanning the QR Code
- Supports Image Upload from Mobile Devices
- Automatically Converts HEIC Images to PNG Format
- Displays Uploaded Images on the Host Page for Easy Download
- Secure Session Management
- Auto-cleanup for Old Files


https://github.com/user-attachments/assets/a021e40d-2edd-43dc-b15e-7ff5beaa8d95


## Technologies Used

- Python (Flask, APScheduler, Werkzeug, Talisman)
- HTML, CSS, JavaScript
- Docker support

## Setup and Installation

### Prerequisites

- Python 3.7+
- Flask 3.0+
- Node.js (optional for front-end building)
- Docker (optional for containerization)
- An appropriate HEIC-to-PNG converter installed on the system.

### Installation Steps

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/username/qr-transfer-app.git
   cd qr-transfer-app
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the necessary folders:

   ```bash
   mkdir -p static/images
   ```

5. Set up environment variables for security:

   - Ensure `app.secret_key` uses a secure token, which you can generate using:
     ```python
     import secrets
     print(secrets.token_urlsafe(16))
     ```
   - Configure any necessary paths or add security configurations, such as HTTPS certificates if used in production.

### Running the Application

1. Start the Flask application:

   ```bash
   python app.py
   ```

2. The application will be accessible at `http://127.0.0.1:8080/` by default. You can configure host and port settings in the `app.py` file if required.

3. Use the `/upload` endpoint to test file upload or simply scan the generated QR code on the index page.

### Docker Deployment (Optional)

To make deployment easier, you can build and run a Docker image:

1. Build the Docker image:

   ```bash
   docker build -t qr-transfer .
   ```

2. Run the Docker container:

   ```bash
   docker run -d -p 8080:8080 qr-transfer
   ```

## Application Structure

- `app.py` - The main entry point for the application, manages routes and logic for QR code generation, file upload, session handling, and health checks.
- `utils/name_generator.py` - Generates unique names for uploaded files.
- `utils/session.py` - Session management class that tracks user sessions and timestamps.
- `utils/heic_processor.py` - Converts HEIC image files to PNG format.
- `templates/` - Folder containing HTML templates for index, upload, and FAQ pages.
- `static/` - Static resources like CSS, JavaScript, and images.
- `requirements.txt` - List of dependencies required to run the application.

## Project Routes

- `/` - Home page that initializes the session, generates a QR code for file upload, and provides file links.
- `/upload` - Handles file uploads and processes HEIC images if needed.
- `/faq` - Displays the FAQ page.
- `/session_links` - JSON response of session-specific images.
- `/health` - Health check endpoint.
- `/reset` - Resets user sessions.

## File Cleanup

To ensure security and prevent server overload, a scheduled background task deletes files older than 5 minutes and clears expired user sessions.

- This task runs using APScheduler, configured to run every 5 minutes.

## Security Features

- **Session Management**: Each user is assigned a unique session managed using UUIDs and cookies.
- **Content Security Policy (CSP)**: Configured to enforce security by allowing specific trusted domains.
- **Secure Upload and File Handling**: File uploads are validated for accepted types and converted securely.

## Usage Tips

- To prevent session expiry issues, ensure the session cookie is preserved when navigating the app.
- Images will be removed after 5 minutes, so download files promptly.
- If you experience errors when uploading, verify that file types are allowed (`png, jpg, jpeg, heic, webp, svg, gif, pdf`).

## FAQ

### How do I start using the app?

Simply open the homepage, scan the QR code to upload a file, and manage uploaded files via the links.

### Are my uploaded files secure?

Uploaded files are stored temporarily and deleted automatically after 5 minutes. Security measures such as CSP and session management are implemented to ensure data safety.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss the proposed modifications.

## License

This project is licensed under the MIT License - see the LICENSE file for details.



Feel free to contact for any feature requests or issues regarding the app.
