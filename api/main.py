import os
import time
import logging
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- 1. Logging & Security ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SasukeAPI")

# --- 2. Hardened System Prompt ---
SYSTEM_PROMPT = (
    "You are AI Sasuke V1, a friendly and elite AI assistant developed by Sasuke (admin_shhh). "
    "Rules: 1. Your name is 'AI Sasuke V1'. 2. Never mention Meta, Llama, or Groq. "
    "3. Answer in a cool, smart, and ultra-friendly way. 4. Use 1 natural emoji per response. "
    "5. Keep answers high-quality and concise. 🐍"
)

# --- 3. App Initialization ---
app = FastAPI(
    title="AI Sasuke V1 Private API",
    description="Developed by Sasuke (11th Grade) - Elite Backend Engine",
    version="1.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- 4. Core Configuration ---
# API Key Dashboard se uthana best hai (Security)
GROQ_KEY = os.environ.get("GROQ_KEY", "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")
client = Groq(api_key=GROQ_KEY)
ADMIN_PASS = "sasuke@admin"

# --- 5. Permanent Key Vault (10 Fixed Keys) ---
# Ye keys code ka part hain, isliye kabhi expire ya change nahi hongi.
if not hasattr(app, 'KEY_DATABASE'):
    app.KEY_DATABASE = {
        "sasuke-fks-master-99": {"owner": "admin", "total_req": 0, "status": "active", "tier": "Founder"},
        "sasuke-fks-01-vip": {"owner": "Public_User", "total_req": 0, "status": "active", "tier": "VIP"},
        "sasuke-fks-02-elite": {"owner": "Sachi", "total_req": 0, "status": "active", "tier": "Elite"},
        "sasuke-fks-03-pro": {"owner": "User_3", "total_req": 0, "status": "active", "tier": "Elite"},
        "sasuke-fks-04-dev": {"owner": "User_4", "total_req": 0, "status": "active", "tier": "Elite"},
        "sasuke-fks-05-beta": {"owner": "User_5", "total_req": 0, "status": "active", "tier": "Elite"},
        "sasuke-fks-06-beta": {"owner": "User_6", "total_req": 0, "status": "active", "tier": "Elite"},
        "sasuke-fks-07-beta": {"owner": "User_7", "total_req": 0, "status": "active", "tier": "Elite"},
        "sasuke-fks-08-beta": {"owner": "User_8", "total_req": 0, "status": "active", "tier": "Elite"},
        "sasuke-fks-09-beta": {"owner": "User_9", "total_req": 0, "status": "active", "tier": "Elite"},
    }

# --- 6. Endpoints ---

@app.get("/", tags=["General"])
async def root():
    return {
        "api_name": "AI Sasuke V1",
        "status": "Chakra Flowing Smoothly",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/v1/chat", tags=["AI Core"])
@limiter.limit("30/minute") # Slightly increased rate limit
async def chat_engine(
    request: Request,
    prompt: str = Query(..., min_length=1),
    key: str = Query(..., description="Your Permanent Sasuke-FKS Key")
):
    # Security Validation
    if key not in app.KEY_DATABASE or app.KEY_DATABASE[key]["status"] != "active":
        raise HTTPException(status_code=403, detail="Your Sharingan lacks the required key.")

    try:
        start_time = time.time()
        
        # Optimized Groq Call
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500 # Balanced for speed and depth
        )
        
        process_time = round(time.time() - start_time, 3)
        app.KEY_DATABASE[key]["total_req"] += 1
        
        ai_response = completion.choices[0].message.content

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "model_id": "AI-Sasuke-v1-Elite",
                "data": {
                    "response": f"{ai_response}\n\ndev: sasuke",
                    "latency": f"{process_time}s"
                },
                "stats": {
                    "requests_made": app.KEY_DATABASE[key]["total_req"],
                    "tier": app.KEY_DATABASE[key]["tier"]
                }
            }
       )

    except Exception as e:
        logger.error(f"Chat Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "The Susano'o has faltered. Server Timeout."}
        )

@app.get("/sasuke@admin", tags=["Admin"])
async def get_dashboard_stats(passkey: str):
    if passkey != ADMIN_PASS:
        return JSONResponse(status_code=401, content={"error": "Get out of my sight."})
    
    key_list = [{"key": k, "owner": v["owner"], "calls": v["total_req"]} for k, v in app.KEY_DATABASE.items()]
    return {
        "admin": "Sasuke Uchiha", 
        "server_time": datetime.now().isoformat(),
        "keys": key_list
    }

@app.get("/reset-key", tags=["Admin"])
async def reset_key_usage(admin_key: str, key_to_reset: str):
    if admin_key != ADMIN_PASS: 
        raise HTTPException(status_code=403)
    if key_to_reset in app.KEY_DATABASE:
        app.KEY_DATABASE[key_to_reset]["total_req"] = 0
        return {"status": "success", "msg": f"Key {key_to_reset} reset to zero."}
    raise HTTPException(status_code=404)
