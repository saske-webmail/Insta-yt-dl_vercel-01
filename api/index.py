import os
import yt_dlp
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIG ---
MASTER_KEY = "sasuke@vpix"
PUBLIC_DAILY_LIMIT = 15
TOTAL_GLOBAL_HITS = 0
IP_DATABASE = {}

# --- PREMIUM UI (TERA ORIGINAL CSS/HTML) ---
CSS_STYLE = """
<style>
    :root { --bg: #080808; --card: #121212; --accent: #0095f6; --text: #ffffff; --dim: #777777; --border: rgba(255, 255, 255, 0.06); --success: #00ff88; }
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
    body { background-color: var(--bg); color: var(--text); display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
    .container { width: 100%; max-width: 450px; padding: 40px 20px; }
    .glass-card { background: var(--card); border: 1px solid var(--border); border-radius: 32px; padding: 45px 30px; text-align: center; box-shadow: 0 30px 60px rgba(0,0,0,0.5); }
    .brand-icon { font-size: 45px; color: var(--accent); margin-bottom: 20px; }
    h1 { font-size: 28px; font-weight: 800; margin-bottom: 8px; }
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }
    .stat-item { background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 18px; padding: 15px; }
    .stat-value { font-size: 18px; font-weight: 700; color: var(--accent); }
    .btn { display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; padding: 18px; border-radius: 16px; font-weight: 700; cursor: pointer; text-decoration: none; border: none; margin-bottom: 12px; }
    .btn-primary { background: var(--text); color: var(--bg); }
    .btn-outline { background: transparent; color: var(--text); border: 1px solid var(--border); }
    .dev-footer { margin-top: 30px; background: rgba(255,255,255,0.01); border: 1px solid var(--border); border-radius: 20px; padding: 15px; display: flex; justify-content: space-between; align-items: center; }
</style>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sasuke Pro API</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {{ css|safe }}
</head>
<body>
    <div class="container">
        <main class="glass-card">
            <div class="brand-icon"><i class="fa-solid fa-bolt-lightning"></i></div>
            <h1>Sasuke API</h1>
            <p style="color:var(--dim); margin-bottom:30px;">Premium Social Extractor</p>
            <div class="stats-grid">
                <div class="stat-item"><span style="font-size:10px; color:var(--dim);">STATUS</span><br><span class="stat-value">ACTIVE</span></div>
                <div class="stat-item"><span style="font-size:10px; color:var(--dim);">HITS</span><br><span class="stat-value">{{ hits }}</span></div>
            </div>
            <a href="#" class="btn btn-primary">VIEW DOCS</a>
            <a href="https://t.me/ah_saske" class="btn btn-outline">CONTACT DEV</a>
            <div class="dev-footer">
                <span style="font-size:12px;">@af.saskee</span>
                <span style="color:var(--accent); font-weight:bold;">V5.0</span>
            </div>
        </main>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, css=CSS_STYLE, hits=TOTAL_GLOBAL_HITS)

@app.route('/api/v5/sasuke/master', methods=['GET'])
def sasuke_extractor():
    global TOTAL_GLOBAL_HITS
    key = request.args.get('key')
    url = request.args.get('url')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if key != MASTER_KEY:
        current_usage = IP_DATABASE.get(user_ip, 0)
        if current_usage >= PUBLIC_DAILY_LIMIT:
            return jsonify({"status": "failed", "msg": "Limit Reached"}), 429
        IP_DATABASE[user_ip] = current_usage + 1

    if not url:
        return jsonify({"status": "failed", "msg": "URL missing"}), 400

    try:
        TOTAL_GLOBAL_HITS += 1
        ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "status": "success",
                "results": {
                    "title": info.get('title'),
                    "download_url": info.get('url'),
                    "thumbnail": info.get('thumbnail')
                },
                "server_hits": TOTAL_GLOBAL_HITS
            })
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

# VERCEL REQUIREMENT
def handler(environ, start_response):
    return app(environ, start_response)
