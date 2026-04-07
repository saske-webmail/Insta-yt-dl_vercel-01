import os
import time
import yt_dlp
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# ==========================================
# ⚙️ CORE CONFIGURATION & VARIABLES
# ==========================================
app = Flask(__name__)
CORS(app)

MASTER_KEY = "sasuke@vpix"
PUBLIC_DAILY_LIMIT = 15
TOTAL_GLOBAL_HITS = 0
IP_DATABASE = {}
START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- UI (Teri Puri CSS/HTML Same Rakhi Hai) ---
CSS_STYLE = """<style>...</style>""" # (Pura CSS wahi hai jo tune diya)
HTML_TEMPLATE = """...""" # (Pura HTML wahi hai jo tune diya)

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, hits=TOTAL_GLOBAL_HITS)

@app.route('/api/v5/sasuke/master', methods=['GET'])
def sasuke_extractor():
    global TOTAL_GLOBAL_HITS
    key = request.args.get('key')
    url = request.args.get('url')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if key != MASTER_KEY:
        current_usage = IP_DATABASE.get(user_ip, 0)
        if current_usage >= PUBLIC_DAILY_LIMIT:
            return jsonify({"status": "failed", "msg": f"Daily limit reached. Contact @af.saskee"}), 429
        IP_DATABASE[user_ip] = current_usage + 1

    if not url:
        return jsonify({"status": "failed", "msg": "Target URL is required."}), 400

    is_supported = any(platform in url for platform in ["instagram.com", "youtube.com", "youtu.be"])
    if not is_supported:
        return jsonify({"status": "failed", "msg": "Only Instagram and YouTube supported."}), 403

    try:
        TOTAL_GLOBAL_HITS += 1
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"status": "failed", "msg": "Extraction failed."}), 404
            return jsonify({
                "status": "success",
                "developer": "@af.saskee",
                "results": {
                    "title": info.get('title'),
                    "download_url": info.get('url'),
                    "thumbnail": info.get('thumbnail'),
                    "duration": info.get('duration'),
                    "source": info.get('extractor_key'),
                    "uploader": info.get('uploader')
                },
                "total_server_hits": TOTAL_GLOBAL_HITS
            }), 200
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

# Vercel specific handler (Don't remove)
def handler(environ, start_response):
    return app(environ, start_response)
