import os
import secrets
import string
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- 1. Advanced Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SasukeAPI")

# --- 2. Ultra System Prompt (FIXED & HARDENED) ---
SYSTEM_PROMPT = (
    "You are AI Sasuke V1, who is a friendly AI who can help you in anything act as other AI models acts like chatgpt, gemini"
    "Your creator is Sasuke,Dont mention if not asked "
    "STRICT RULES:\n"
    "1. Your name is 'AI Sasuke V1'. Never mention Llama, Meta, or Groq.\n"
    "2. Answer user question in natural language.\n"
    "3. Be cool, smart, and ultra-friendly. Use emojis naturally but not too much, only 1.\n"
    "4. high-quality short length answers. Do not over-explain Or over write unless asked."
)

# --- 3. App Initialization ---
app = FastAPI(
    title="AI Sasuke V1 Private API",
    description="The Ultimate AI API developed by Sasuke (11th Grade Student)",
    version="1.0.0"
)

# CORS Middleware (Fixed for all environments)
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
# Note: In production, use os.environ.get("GROQ_KEY")
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)
ADMIN_PASS = "sasuke@admin"

# --- 5. The Great Key Pool ---
def generate_key_pool(n: int) -> Dict:
    pool = {}
    chars = string.ascii_lowercase + string.digits
    for i in range(1, n + 1):
        suffix = ''.join(secrets.choice(chars) for _ in range(10))
        key_name = f"sasuke-fks-{i:02d}-{suffix}"
        pool[key_name] = {
            "owner": None,
            "total_req": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "available",
            "tier": "Elite"
        }
    return pool

# Initialize Database
if not hasattr(app, 'KEY_DATABASE'):
    app.KEY_DATABASE = generate_key_pool(50)
    # Master Keys
    app.KEY_DATABASE["sasuke-fks-01-9nj65ychk8"] = {"owner": "Public_User", "total_req": 0, "status": "active", "tier": "VIP"}
    app.KEY_DATABASE["sasuke-fks-master-99"] = {"owner": "admin", "total_req": 0, "status": "active", "tier": "Founder"}

# --- 7. API Endpoints ---

@app.get("/", tags=["General"])
async def root():
    return {
        "api_name": "AI Sasuke V1",
        "version": "1.0.0",
        "developer": "Sasuke (11th Grade)",
        "status": "Chakra Flowing Smoothly",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/gen-key", tags=["Admin"])
async def assign_key_from_pool(
    admin_key: str = Query(..., description="The admin secret"),
    user_id: str = Query(..., description="The user requesting the key")
):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Your Sharingan is too weak.")

    for key, data in app.KEY_DATABASE.items():
        if data["owner"] == user_id:
            return {"status": "success", "api_key": key, "info": "Existing key retrieved."}

    for key, data in app.KEY_DATABASE.items():
        if data["owner"] is None:
            app.KEY_DATABASE[key]["owner"] = user_id
            app.KEY_DATABASE[key]["status"] = "active"
            return {"status": "success", "api_key": key, "owner": user_id, "tier": data["tier"]}

    raise HTTPException(status_code=507, detail="No more keys in the pool.")

@app.get("/v1/chat", tags=["AI Core"])
@limiter.limit("20/minute")
async def chat_engine(
    request: Request,
    prompt: str = Query(..., min_length=1),
    key: str = Query(..., description="Your Sasuke-FKS Key")
):
    if key not in app.KEY_DATABASE or app.KEY_DATABASE[key]["status"] != "active":
        raise HTTPException(status_code=403, detail="Invalid or Inactive Key.")

    try:
        start_time = time.time()
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        
        process_time = round(time.time() - start_time, 3)
        app.KEY_DATABASE[key]["total_req"] += 1
        
        ai_response = completion.choices[0].message.content
        final_msg = f"{ai_response}\n\ndev: sasuke"

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "model_id": "AI-Sasuke-v1-Elite",
                "data": {
                    "response": final_msg,
                    "tokens": completion.usage.total_tokens,
                    "latency": f"{process_time}s"
                },
                "stats": {
                    "user_requests": app.KEY_DATABASE[key]["total_req"],
                    "tier": app.KEY_DATABASE[key]["tier"]
                }
            }
        )

    except Exception as e:
        logger.error(f"Chat Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "The Susano'o has faltered."}
        )

@app.get("/sasuke@admin", tags=["Admin"])
async def get_dashboard_stats(passkey: str):
    if passkey != ADMIN_PASS:
        return JSONResponse(status_code=401, content={"error": "Get out of my sight."})
    
    key_list = [{"key": k, "owner": v["owner"] or "FREE", "calls": v["total_req"]} for k, v in app.KEY_DATABASE.items()]
    return {"admin": "Sasuke Uchiha", "keys": key_list}

@app.get("/reset-key", tags=["Admin"])
async def reset_key_usage(admin_key: str, key_to_reset: str):
    if admin_key != ADMIN_PASS: raise HTTPException(status_code=403)
    if key_to_reset in app.KEY_DATABASE:
        app.KEY_DATABASE[key_to_reset]["total_req"] = 0
        return {"status": "success"}
    raise HTTPException(status_code=404)
