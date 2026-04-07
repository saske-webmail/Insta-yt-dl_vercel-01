import os
import yt_dlp
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

# ==========================================
# 🚀 INITIALIZATION
# ==========================================
app = Flask(__name__)
CORS(app)

# Global constants
MASTER_KEY = "sasuke@vpix"
ADMIN_NAME = "@af.saskee"
SERVER_START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TOTAL_HITS = 0

# ==========================================
# 🎨 PREMIUM DASHBOARD UI (HTML/CSS)
# ==========================================
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    :root { --bg: #050505; --card: #0f0f0f; --accent: #ff0000; --text: #ffffff; --dim: #a0a0a0; --border: rgba(255,255,255,0.08); }
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .main-card { background: var(--card); border: 1px solid var(--border); border-radius: 30px; padding: 40px; text-align: center; width: 90%; max-width: 450px; box-shadow: 0 40px 100px rgba(0,0,0,0.8); position: relative; overflow: hidden; }
    .main-card::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,0,0,0.05) 0%, transparent 70%); z-index: 0; }
    .content { position: relative; z-index: 1; }
    i.fa-youtube { font-size: 60px; color: var(--accent); margin-bottom: 20px; filter: drop-shadow(0 0 15px rgba(255,0,0,0.4)); }
    h1 { font-size: 28px; font-weight: 800; letter-spacing: -1px; margin-bottom: 10px; }
    .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 25px 0; }
    .s-box { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 15px; border: 1px solid var(--border); }
    .s-label { font-size: 10px; color: var(--dim); text-transform: uppercase; }
    .s-val { font-size: 18px; font-weight: 700; display: block; margin-top: 5px; }
    .btn { display: block; width: 100%; padding: 15px; border-radius: 15px; text-decoration: none; font-weight: 700; margin-top: 10px; transition: 0.3s; }
    .btn-red { background: var(--accent); color: white; }
    .btn-outline { border: 1px solid var(--border); color: white; font-size: 14px; }
    .btn:hover { transform: translateY(-3px); opacity: 0.9; }
    .footer { margin-top: 30px; font-size: 11px; color: var(--dim); }
</style>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sasuke YT V5 | Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {{ css|safe }}
</head>
<body>
    <div class="main-card">
        <div class="content">
            <i class="fa-brands fa-youtube"></i>
            <h1>SASUKE YT V5</h1>
            <p style="color:var(--dim); font-size: 14px;">Premium 2026 Engine Active</p>
            
            <div class="stats">
                <div class="s-box">
                    <span class="s-label">Status</span>
                    <span class="s-val" style="color:#00ff88;">ONLINE</span>
                </div>
                <div class="s-box">
                    <span class="s-label">Total Hits</span>
                    <span class="s-val">{{ hits }}</span>
                </div>
            </div>

            <a href="#" class="btn btn-red">API IS ACTIVE</a>
            <a href="https://instagram.com/af.saskee" class="btn btn-outline">Developer: {{ admin }}</a>

            <div class="footer">
                <p>Server Started: {{ uptime }}</p>
                <p style="margin-top:5px; opacity:0.5;">Powered by Sasuke Cloud Engine</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# 🛠️ CORE EXTRACTOR LOGIC
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, css=CSS_STYLE, hits=TOTAL_HITS, uptime=SERVER_START_TIME, admin=ADMIN_NAME)

@app.route('/api/v5/sasuke/yt', methods=['GET'])
def youtube_api():
    global TOTAL_HITS
    url = request.args.get('url')
    key = request.args.get('key')

    # Simple Key Check (Optional)
    if key != MASTER_KEY:
        return jsonify({"status": "failed", "msg": "Invalid Master Key"}), 403

    if not url:
        return jsonify({"status": "failed", "msg": "No URL provided"}), 400

    try:
        TOTAL_HITS += 1
        
        # Path to cookies.txt (Must be in root folder on GitHub)
        cookie_path = os.path.join(os.getcwd(), 'cookies.txt')

        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'cookiefile': cookie_path if os.path.exists(cookie_path) else None,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Format extraction
            formats_data = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('url'):
                    formats_data.append({
                        "quality": f.get('resolution') or f.get('format_note'),
                        "ext": f.get('ext'),
                        "size": f"{round(f.get('filesize', 0) / 1048576, 2)} MB" if f.get('filesize') else "N/A",
                        "url": f.get('url')
                    })

            return jsonify({
                "status": "success",
                "developer": ADMIN_NAME,
                "metadata": {
                    "title": info.get('title'),
                    "thumbnail": info.get('thumbnail'),
                    "channel": info.get('uploader'),
                    "duration": f"{info.get('duration')}s",
                    "views": info.get('view_count')
                },
                "download": {
                    "best_link": info.get('url'),
                    "all_qualities": formats_data[:8] # Send top 8 formats
                }
            }), 200

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

# ==========================================
# 🚀 VERCEL HANDLER (CRITICAL FIX)
# ==========================================

# Vercel looks for 'app' at the top level
app = app

# Ensure external handler support
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
