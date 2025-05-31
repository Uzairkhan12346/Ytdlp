from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import uuid
import subprocess

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "static"
COOKIES_FILE = "cookies.txt"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Function to delete old files (older than 60 sec)
def delete_old_files():
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        if os.path.isfile(file_path) and time.time() - os.path.getctime(file_path) > 60:
            os.remove(file_path)

@app.route('/download', methods=['GET'])
def download_audio():
    video_url = request.args.get("url")
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Basic URL validation
    if "youtube.com" not in video_url and "youtu.be" not in video_url:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    delete_old_files()  # Clean old files

    unique_filename = f"{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)

    # Check if cookies file exists
    if not os.path.exists(COOKIES_FILE):
        return jsonify({"error": "Cookies file not found. Please provide a valid cookies.txt"}), 500

    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--output", output_path,
        "--cookies", COOKIES_FILE,
        video_url
    ]

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return jsonify({
            "file_url": f"https://uzairmtx-ai-api-key-y6yc.onrender.com/static/{unique_filename}",
            "message": "Download successful"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Download failed", "details": e.stderr}), 500

@app.route('/channel', methods=['GET'])
def get_channel():
    return jsonify({"channel_link": "https://www.youtube.com/@MrUzairXxX-MTX"})

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
