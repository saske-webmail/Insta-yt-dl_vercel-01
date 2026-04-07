import os
import yt_dlp
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==========================================
# ⚙️ CONFIGURATION & AUTH
# ==========================================
MASTER_KEY = "sasuke@vpix"
ADMIN_NAME = "@af.saskee"
SERVER_START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TOTAL_HITS = 0

# ==========================================
# 🎨 UI: PREMIUM DARK DASHBOARD (300+ Lines Scope)
# ==========================================
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    :root {
        --bg: #050505;
        --card: #0f0f0f;
        --accent: #ff0000; /* YouTube Red */
        --accent-glow: rgba(255, 0, 0, 0.2);
        --text-main: #ffffff;
        --text-dim: #a0a0a0;
        --border: rgba(255, 255, 255, 0.08);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
    
    body {
        background-color: var(--bg);
        color: var(--text-main);
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        overflow-x: hidden;
    }

    .dashboard {
        width: 100%;
        max-width: 500px;
        padding: 20px;
        position: relative;
    }

    /* Background Glow Effects */
    .glow {
        position: absolute;
        width: 300px;
        height: 300px;
        background: var(--accent-glow);
        filter: blur(120px);
        z-index: -1;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }

    .main-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 35px;
        padding: 40px;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 40px 100px rgba(0,0,0,0.8);
    }

    .logo-area i {
        font-size: 50px;
        color: var(--accent);
        margin-bottom: 20px;
        filter: drop-shadow(0 0 15px var(--accent));
    }

    h1 { font-size: 32px; font-weight: 800; margin-bottom: 5px; letter-spacing: -1px; }
    .subtitle { color: var(--text-dim); font-size: 14px; margin-bottom: 30px; }

    .stats-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-bottom: 25px;
    }

    .stat-box {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        padding: 20px;
        border-radius: 20px;
        transition: 0.3s;
    }

    .stat-box:hover { border-color: var(--accent); transform: translateY(-5px); }
    .stat-label { font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { font-size: 20px; font-weight: 700; display: block; margin-top: 5px; }

    .info-list {
        text-align: left;
        background: rgba(0,0,0,0.2);
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 25px;
    }

    .info-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        font-size: 13px;
        border-bottom: 1px solid var(--border);
    }

    .info-item:last-child { border: none; }
    .info-key { color: var(--text-dim); }

    .btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        padding: 20px;
        border-radius: 20px;
        font-weight: 700;
        text-decoration: none;
        transition: 0.3s;
        margin-bottom: 10px;
    }

    .btn-main { background: var(--accent); color: white; box-shadow: 0 10px 20px rgba(255,0,0,0.2); }
    .btn-main:hover { opacity: 0.9; transform: scale(1.02); }
    .btn-sub { background: transparent; color: white; border: 1px solid var(--border); }
    .btn-sub:hover { background: rgba(255,255,255,0.05); }

    .footer {
        margin-top: 25px;
        font-size: 12px;
        color: var(--text-dim);
    }

    .badge {
        background: rgba(255,0,0,0.1);
        color: var(--accent);
        padding: 4px 10px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 10px;
    }
</style>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sasuke YT Downloader Pro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {{ css|safe }}
</head>
<body>
    <div class="glow"></div>
    <div class="dashboard">
        <div class="main-card">
            <div class="logo-area">
                <i class="fa-brands fa-youtube"></i>
            </div>
            <h1>Sasuke YT V5</h1>
            <p class="subtitle">Ultimate High-Quality Media Extractor</p>

            <div class="stats-container">
                <div class="stat-box">
                    <span class="stat-label">System Status</span>
                    <span class="stat-value" style="color: #00ff88;">ONLINE</span>
                </div>
                <div class="stat-box">
                    <span class="stat-label">Total API Hits</span>
                    <span class="stat-value">{{ hits }}</span>
                </div>
            </div>

            <div class="info-list">
                <div class="info-item">
                    <span class="info-key">Engine Version</span>
                    <span class="info-val">yt-dlp (Stable)</span>
                </div>
                <div class="info-item">
                    <span class="info-key">Authentication</span>
                    <span class="info-val">Cookies Active <i class="fa-solid fa-cookie-bite"></i></span>
                </div>
                <div class="info-item">
                    <span class="info-key">Server Uptime</span>
                    <span class="info-val">100% Guaranteed</span>
                </div>
            </div>

            <a href="https://t.me/ah_saske" class="btn btn-main">
                <i class="fa-brands fa-telegram"></i> JOIN CHANNEL
            </a>
            <a href="https://instagram.com/af.saskee" class="btn btn-sub">
                <i class="fa-brands fa-instagram"></i> DEVELOPER
            </a>

            <div class="footer">
                <p>Built with ❤️ by <span style="color:white;">Sasuke</span></p>
                <p style="font-size: 10px; margin-top:5px; opacity:0.5;">Uptime: {{ uptime }}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# 🚀 CORE EXTRACTOR LOGIC
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, css=CSS_STYLE, hits=TOTAL_HITS, uptime=SERVER_START_TIME)

@app.route('/api/v5/sasuke/yt', methods=['GET'])
def youtube_downloader():
    global TOTAL_HITS
    key = request.args.get('key')
    url = request.args.get('url')

    if not url:
        return jsonify({"status": "failed", "msg": "No
