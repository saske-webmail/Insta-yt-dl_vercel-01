import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# ⚙️ CORE CONFIGURATION
# ==========================================
MASTER_KEY = "sasuke@vpix"      # Teri Private Key
PUBLIC_DAILY_LIMIT = 15        # Bina key ke limit
TOTAL_GLOBAL_HITS = 0          # Hits counter
IP_DATABASE = {}               # IP tracking

# ==========================================
# 🎨 PREMIUM BLACK AESTHETIC UI
# ==========================================
CSS_STYLE = """
<style>
    :root {
        --bg: #080808;
        --card: #121212;
        --accent: #0095f6;
        --text: #ffffff;
        --dim: #777777;
        --border: rgba(255, 255, 255, 0.06);
        --success: #00ff88;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
    body {
        background-color: var(--bg);
        color: var(--text);
        display: flex;
        flex-direction: column;
        align-items: center;
        min-height: 100vh;
    }
    .container { width: 100%; max-width: 450px; padding: 40px 20px; }
    .glass-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 32px;
        padding: 45px 30px;
        text-align: center;
        box-shadow: 0 30px 60px rgba(0,0,0,0.5);
    }
    .brand-icon { font-size: 45px; color: var(--accent); margin-bottom: 20px; }
    h1 { font-size: 28px; font-weight: 800; margin-bottom: 8px; letter-spacing: -1px; }
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }
    .stat-item { background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 18px; padding: 15px; }
    .stat-label { font-size: 10px; color: var(--dim); text-transform: uppercase; display: block; margin-bottom: 5px; }
    .stat-value { font-size: 18px; font-weight: 700; color: var(--accent); }
    .btn {
        display: flex; align-items: center; justify-content: center; gap: 10px;
        width: 100%; padding: 18px; border-radius: 16px; font-weight: 700;
        cursor: pointer; text-decoration: none; border: none; margin-bottom: 12px;
    }
    .btn-primary { background: var(--text); color: var(--bg); }
    .btn-outline { background: transparent; color: var(--text); border: 1px solid var(--border); }
    .dev-footer {
        margin-top: 30px; background: rgba(255,255,255,0.01);
        border: 1px solid var(--border); border-radius: 20px; padding: 15px;
        display: flex; justify-content: space-between; align-items: center;
    }
</style>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sasuke Pro API | V10</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    {{ css|safe }}
</head>
<body>
    <div class="container">
        <main class="glass-card">
            <div class="brand-icon"><i class="fa-solid fa-bolt-lightning"></i></div>
            <h1>Sasuke API</h1>
            <p style="color:var(--dim); margin-bottom:30px; font-size: 14px;">Stable Social Media Extractor</p>
            
            <div class="stats-grid">
                <div class="stat-item"><span class="stat-label">System</span><span class="stat-value">v10.0</span></div>
                <div class="stat-item"><span class="stat-label">Total Hits</span><span class="stat-value">{{ hits }}</span></div>
            </div>

            <div style="background:rgba(0,149,246,0.1); border-radius:12px; padding:10px; margin-bottom:20px; font-size:11px; color:var(--accent);">
                <i class="fa-solid fa-check-circle"></i> Cobalt Engine Successfully Updated
            </div>

            <a href="https://t.me/ah_saske" class="btn btn-primary">GET MASTER KEY</a>
            <a href="https://instagram.com/af.saskee" class="btn btn-outline">FOLLOW DEVELOPER</a>

            <div class="dev-footer">
                <span style="font-size:12px; font-weight:600;">@af.saskee</span>
                <span style="color:var(--dim); font-size:10px;">SASUKE ENGINE</span>
            </div>
        </main>
    </div>
</body>
</html>
"""

# ==========================================
# 🚀 API ROUTES
# ==========================================

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, css=CSS_STYLE, hits=TOTAL_GLOBAL_HITS)

@app.route('/api/v5/sasuke/master', methods=['GET'])
def sasuke_extractor():
    global TOTAL_GLOBAL_HITS
    
    key = request.args.get('key')
    url = request.args.get('url')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # 1. Access Control
    if key != MASTER_KEY:
        current_usage = IP_DATABASE.get(user_ip, 0)
        if current_usage >= PUBLIC_DAILY_LIMIT:
            return jsonify({"status": "failed", "msg": f"Limit of {PUBLIC_DAILY_LIMIT} reached"}), 429
        IP_DATABASE[user_ip] = current_usage + 1

    if not url:
        return jsonify({"status": "failed", "msg": "URL is required"}), 400

    # 2. NEW Cobalt v10 Extraction Logic
    try:
        TOTAL_GLOBAL_HITS += 1
        
        # Updated Payload for v10
        cobalt_payload = {
            "url": url,
            "videoQuality": "720",
            "filenameStyle": "pretty",
            "downloadMode": "auto"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Request to Cobalt API
        r = requests.post("https://api.cobalt.tools/", json=cobalt_payload, headers=headers)
        
        # Pehle check karo ki request successful hui ya nahi
        if r.status_code != 200:
            return jsonify({"status": "failed", "msg": "Cobalt API is currently busy or down."}), r.status_code
            
        response_data = r.json()

        if response_data.get('status') == 'error':
            return jsonify({"status": "failed", "msg": response_data.get('text', 'Extraction error')}), 400

        # Success Response
        return jsonify({
            "status": "success",
            "developer": "@af.saskee",
            "results": {
                "download_url": response_data.get('url'),
                "type": response_data.get('status'),
                "filename": response_data.get('filename', 'video')
            },
            "server_hits": TOTAL_GLOBAL_HITS
        }), 200

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

# ==========================================
# ⚙️ VERCEL ENTRY POINT
# ==========================================
def handler(environ, start_response):
    return app(environ, start_response)
