import os
import yt_dlp
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

# Vercel looks for 'app' or 'handler'
app = Flask(__name__)
CORS(app)

# --- Configuration ---
MASTER_KEY = "sasuke@vpix"
ADMIN_NAME = "@af.saskee"
START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
HITS = 0

# --- Dashboard UI ---
UI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sasuke YT V5</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #050505; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #0f0f0f; border: 1px solid #333; padding: 30px; border-radius: 20px; text-align: center; width: 350px; }
        i { font-size: 50px; color: red; margin-bottom: 10px; }
        h1 { margin: 10px 0; font-size: 24px; }
        .stat { color: #888; font-size: 14px; margin-bottom: 20px; }
        .btn { display: block; background: red; color: white; text-decoration: none; padding: 12px; border-radius: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <i class="fa-brands fa-youtube"></i>
        <h1>SASUKE YT V5</h1>
        <div class="stat">Status: <span style="color:lime">ONLINE</span> | Hits: {{ hits }}</div>
        <a href="https://instagram.com/af.saskee" class="btn">CONTACT DEVELOPER</a>
        <p style="font-size:10px; color:#444; margin-top:15px;">Uptime: {{ uptime }}</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(UI_TEMPLATE, hits=HITS, uptime=START_TIME)

@app.route('/api/v5/sasuke/yt', methods=['GET'])
def yt_api():
    global HITS
    url = request.args.get('url')
    key = request.args.get('key')

    if key != MASTER_KEY:
        return jsonify({"status": "failed", "msg": "Wrong Key"}), 403
    if not url:
        return jsonify({"status": "failed", "msg": "No URL"}), 400

    try:
        HITS += 1
        cookie_path = os.path.join(os.getcwd(), 'cookies.txt')
        
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'cookiefile': cookie_path if os.path.exists(cookie_path) else None,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "status": "success",
                "metadata": {
                    "title": info.get('title'),
                    "thumbnail": info.get('thumbnail'),
                    "channel": info.get('uploader')
                },
                "download": info.get('url')
            })
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

# DO NOT MOVE THIS: Vercel handler
app = app
