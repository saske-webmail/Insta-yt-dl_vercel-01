import os
import yt_dlp
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

# Vercel looks for 'app' or 'handler'
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import yt_dlp
from datetime import datetime

# VERCEL REQUIRES THIS AT TOP LEVEL
app = Flask(__name__)
CORS(app)
handler = app # Explicitly defining handler for Vercel

# --- CONFIGURATION ---
MASTER_KEY = "sasuke@vpix"
ADMIN_NAME = "@af.saskee"
START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
HITS = 0

# --- DASHBOARD UI ---
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sasuke YT V5</title>
    <style>
        body { background: #050505; color: white; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #111; border: 1px solid #333; padding: 40px; border-radius: 25px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #ff0000; margin-bottom: 5px; }
        .status { color: #00ff88; font-weight: bold; font-size: 14px; text-transform: uppercase; }
        .hits { margin: 20px 0; font-size: 18px; color: #aaa; }
        .footer { font-size: 12px; color: #555; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>SASUKE YT V5</h1>
        <div class="status">● System Active</div>
        <div class="hits">Total Server Hits: {{ hits }}</div>
        <p>Developer: {{ admin }}</p>
        <div class="footer">Server Started: {{ uptime }}</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(UI_HTML, hits=HITS, admin=ADMIN_NAME, uptime=START_TIME)

@app.route('/api/v5/sasuke/yt', methods=['GET'])
def yt_downloader():
    global HITS
    url = request.args.get('url')
    key = request.args.get('key')

    if key != MASTER_KEY:
        return jsonify({"status": "failed", "msg": "Invalid Key"}), 403
    if not url:
        return jsonify({"status": "failed", "msg": "URL missing"}), 400

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
                    "channel": info.get('uploader'),
                    "views": info.get('view_count')
                },
                "download_url": info.get('url')
            })
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

# DO NOT DELETE: Extra safety for Vercel
application = app
