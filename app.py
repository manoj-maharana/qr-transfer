# Flask application setup for image upload and session management
from typing import Dict
from flask import Flask, Response, json, make_response, render_template, request, redirect, send_from_directory, url_for, jsonify
from werkzeug.utils import secure_filename

# Modules for file handling and scheduling
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# QR code and base64 management
import os
import qrcode
from io import BytesIO
import base64

# Session handling and threading for background tasks
from utils.session import Session
from threading import Thread

# Import utility functions for filename generation and image conversion
from utils.name_generator import create_unique_filename
from utils.heic_processor import transform_heic_to_png

# Unique ID and timestamp management
import uuid

# Security configurations
from flask_talisman import Talisman
from config.security import talisman_policies
import secrets

ACCEPTED_FILETYPES = set(["png", "jpg", "jpeg", "heic", "webp", "svg", "gif", "pdf"])

# Flask app initialization
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # Max upload size 16 MB

# Security headers configuration
csp = {
    'default-src': ["'self'", 'fonts.googleapis.com', '*.google-analytics.com', 'fonts.gstatic.com', 'cdnjs.cloudflare.com'],
    'img-src': ['*', 'data:', 'blob:', '*.google-analytics.com', '*.googletagmanager.com', '*.buymeacoffee.com'],
    'script-src': ["'self'", "'unsafe-inline'", '*.google-analytics.com', '*.googletagmanager.com', '*.buymeacoffee.com'],
    'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com', 'cdnjs.cloudflare.com'],
    'frame-src': ['www.buymeacoffee.com', 'buymeacoffee.com', "'self'"]
}

# Apply security policies using Talisman
talisman = Talisman(app)
for key, value in talisman_policies.items():
    setattr(talisman, key, value)
talisman.content_security_policy = csp

def derive_url_root(request):
    """Returns the root URL, accommodating reverse proxies if in use."""
    return request.headers.get("X-Full-Request-URL", request.url_root)

# Global storage for URL root and active sessions
GLOBAL_URL_ROOT = None
sessions: Dict[str, Session] = {}

def delete_old_files():
    """Cleans up files older than 5 minutes and removes outdated sessions."""
    now = datetime.now()
    expired_sessions = []
    
    for session_id, session in sessions.items():
        if now - session.timestamp > timedelta(minutes=5):
            for image_url in session.images:
                image_filename = image_url.split("/")[-1]
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del sessions[session_id]
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(path) and not path.endswith('.gitkeep'):
            creation_time = datetime.fromtimestamp(os.path.getctime(path))
            if now - creation_time > timedelta(minutes=5):
                os.remove(path)

# Schedule file cleanup every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_files, "interval", minutes=5)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    """Sets up the user session, generates a QR code for upload, and renders the home page."""
    user_id_cookie = request.cookies.get('user_id')
    if not user_id_cookie or user_id_cookie not in sessions:
        user_id = str(uuid.uuid4())
        sessions[user_id] = Session(user_id)
    else:
        user_id = user_id_cookie

    qr = qrcode.QRCode(
        version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4
    )
    global GLOBAL_URL_ROOT
    GLOBAL_URL_ROOT = derive_url_root(request)
    upload_url = f'{GLOBAL_URL_ROOT}upload?session_id={user_id}'
    qr.add_data(upload_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000", back_color="#ffffff")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    rendered_template = render_template('index.html', qr_code_data=img_str, qr_code_url=upload_url, session=user_id)
    response = make_response(rendered_template)
    if not user_id_cookie or user_id_cookie != user_id:
        response.set_cookie('user_id', user_id)
    return response

@app.route('/health')
def health():
    """Health check endpoint."""
    return 'ok'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handles file uploads, validates file types, and processes HEIC files if required."""
    session_id = request.args.get('session_id', '')
    if session_id not in sessions:
        return make_response('<h1>Invalid session, press "Reset Session" button on the main page and try again</h1>')

    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename:
            return render_template('upload.html', error='Please upload a file')
        
        file_extension = file.filename.rsplit('.', 1)[-1].lower()
        if file_extension not in ACCEPTED_FILETYPES:
            return render_template('upload.html', error=f'Error: {file_extension} extension is not supported.')

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        saved_filename = f"{session_id}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(file_path)

        if saved_filename.lower().endswith('.heic'):
            def heic_conversion_task():
                png_path = transform_heic_to_png(file_path)
                new_filename = saved_filename.rsplit('.', 1)[0] + '.png'
                if session_id in sessions:
                    sessions[session_id].add_image(f'{GLOBAL_URL_ROOT}static/images/{new_filename}')
                    sessions[session_id].loading_count -= 1
            thread = Thread(target=heic_conversion_task)
            sessions[session_id].loading_count += 1
            thread.start()
        else:
            sessions[session_id].add_image(f'{GLOBAL_URL_ROOT}static/images/{saved_filename}')
    return render_template('upload.html')

@app.route('/faq', methods=['GET'])
def faq():
    """Renders the FAQ page."""
    return render_template('faq.html')

@app.route('/session_links', methods=['GET'])
def get_session_links():
    """Provides a list of uploaded images for the session."""
    session_id = request.args.get('session_id')
    if not session_id:
        return make_response('Missing query param "session_id"', 400)
    if session_id not in sessions:
        return make_response('Session not found with provided ID', 404)

    return jsonify({
        "images": sessions[session_id].images,
        "loading_count": sessions[session_id].loading_count
    })

@app.route('/counter')
def get_counter():
    """Returns the current count of uploaded files."""
    counter_file = 'static/counter.txt'
    if not os.path.exists(counter_file):
        with open(counter_file, 'w') as f:
            f.write('0')
    with open(counter_file, 'r') as f:
        count = f.read()
    return count

@app.route('/static/images/<path:filename>', methods=['GET'])
def get_image(filename):
    """Serves images from the static/images directory, enforcing access control."""
    hidden_filenames = [".gitignore"]
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if filename not in hidden_filenames and os.path.exists(full_path):
        file_extension = filename.rsplit('.', 1)[-1] if '.' in filename else None
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, download_name=create_unique_filename(file_extension))
    return Response(json.dumps({"message": "File not found."}), status=404, mimetype='application/json')

@app.route('/reset')
def reset_session():
    """Clears the current session and resets user cookies."""
    user_id_cookie = request.cookies.get('user_id')
    if user_id_cookie in sessions:
        del sessions[user_id_cookie]
    response = make_response(redirect(url_for('index')))
    response.set_cookie('user_id', '', expires=0)
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
