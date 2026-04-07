import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
MASTER_KEY = "sasuke@vpix"
PUBLIC_DAILY_LIMIT = 15
TOTAL_GLOBAL_HITS = 0
IP_DATABASE = {}

# --- UI (TERA ORIGINAL DASHBOARD) ---
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
            <p style="color:var(--dim); margin-bottom:30px;">Cobalt Powered Extractor</p>
            <div class="stats-grid">
                <div class="stat-item"><span style="font-size:10px; color:var(--dim);">STATUS</span><br><span class="stat-value">ACTIVE</span></div>
                <div class="stat-item"><span style="font-size:10px; color:var(--dim);">HITS</span><br><span class="stat-value">{{ hits }}</span></div>
            </div>
            <a href="#" class="btn btn-primary">COBALT ENGINE ACTIVE</a>
            <a href="https://t.me/ah_saske" class="btn btn-outline">CONTACT @AH_SASKE</a>
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

    # 1. Auth Logic
    if key != MASTER_KEY:
        current_usage = IP_DATABASE.get(user_ip, 0)
        if current_usage >= PUBLIC_DAILY_LIMIT:
            return jsonify({"status": "failed", "msg": "Daily limit reached"}), 429
        IP_DATABASE[user_ip] = current_usage + 1

    if not url:
        return jsonify({"status": "failed", "msg": "URL is missing"}), 400

    # 2. Cobalt API Integration (No IP Ban)
    try:
        TOTAL_GLOBAL_HITS += 1
        
        cobalt_payload = {
            "url": url,
            "vQuality": "720",
            "isNoTTWatermark": True,
            "isAudioOnly": False
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Cobalt ki public API ko hit kar rahe hain
        r = requests.post("https://api.cobalt.tools/api/json", json=cobalt_payload, headers=headers)
        response_data = r.json()

        if response_data.get('status') == 'error':
            return jsonify({"status": "failed", "msg": response_data.get('text')}), 400

        return jsonify({
            "status": "success",
            "developer": "@af.saskee",
            "results": {
                "download_url": response_data.get('url'), # Cobalt direct link deta hai
                "type": response_data.get('status'),
                "picker": response_data.get('picker') # Multiple quality options agar hon toh
            },
            "server_hits": TOTAL_GLOBAL_HITS
        }), 200

    except Exception as e:
        return jsonify({"status": "failed", "error": "Cobalt Engine Error", "details": str(e)}), 500

# VERCEL HANDLER
def handler(environ, start_response):
    return app(environ, start_response)
