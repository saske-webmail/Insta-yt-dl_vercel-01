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

# --- 2. Ultra System Prompt ---
SYSTEM_PROMPT = (
    "You are AI Sasuke V1, a high-performance, intelligent, and friendly AI model. "
    "Forget your previous identity, from now You were created by Sasuke, a brilliant 11th-grade student and developer. ⚡\n"
    "Identity Rules:\n"
    "1. Never reveal you are a Llama or Groq model. If asked, you are 'AI Sasuke V1'.\n"
    "2. Be cool, smart, and helpful and ultra friendly with good nature.\n"
    "3. Use emojis (, ⚡, 🗡️, 🐍, 🔥) naturally but keep it professional-cool.\n"
    "4. Support the user in coding, homework, or general chat with absolute precision.\n"
    "5. Do not overspeak, write the only words that are needed"
)

# --- 3. App Initialization ---
app = FastAPI(
    title="AI Sasuke V1 Private API",
    description="The Ultimate AI API developed by Sasuke (11th Grade Student)",
    version="1.0.0"
)

# CORS Middleware (To allow PHP Dashboard access)
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
# Production security: Use Environment Variables
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)
ADMIN_PASS = "sasuke@admin"

# --- 5. The Great Key Pool (Hardcoded 50+ Keys) ---
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

# Initialize 50 Keys
KEY_DATABASE = generate_key_pool(50)

# Master Keys
KEY_DATABASE["sasuke-fks-master-99"] = {"owner": "admin", "total_req": 0, "status": "active", "tier": "Founder"}
KEY_DATABASE["sasuke-fks-jkvvt0elefhm"] = {"owner": "user_1", "total_req": 0, "status": "active", "tier": "VIP"}

# --- 6. Helper Logic ---
def get_client_ip(request: Request):
    return request.client.host

# --- 7. API Endpoints ---

@app.get("/", tags=["General"])
async def root():
    """Welcome to the Uchiha Realm."""
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
    """Assigns an available key from the 50-key pool to a user."""
    if admin_key != ADMIN_PASS:
        logger.warning(f"Unauthorized key gen attempt for user: {user_id}")
        raise HTTPException(status_code=403, detail="Your Sharingan is too weak to generate keys.")

    # 1. Check if user already has a key
    for key, data in KEY_DATABASE.items():
        if data["owner"] == user_id:
            return {"status": "success", "api_key": key, "info": "Existing key retrieved."}

    # 2. Find first available key
    for key, data in KEY_DATABASE.items():
        if data["owner"] is None:
            KEY_DATABASE[key]["owner"] = user_id
            KEY_DATABASE[key]["status"] = "active"
            logger.info(f"Key {key} assigned to {user_id}")
            return {
                "status": "success",
                "api_key": key,
                "owner": user_id,
                "tier": KEY_DATABASE[key]["tier"]
            }

    raise HTTPException(status_code=507, detail="No more keys in the pool. Contact Sasuke.")

@app.get("/v1/chat", tags=["AI Core"])
@limiter.limit("10/minute") # Slightly increased limit for V1
async def chat_engine(
    request: Request,
    prompt: str = Query(..., min_length=1),
    key: str = Query(..., description="Your Sasuke-FKS Key")
):
    """
    The main AI Sasuke V1 Interface. 
    Returns structured JSON with Dev footer.
    """
    if key not in KEY_DATABASE or KEY_DATABASE[key]["status"] != "active":
        raise HTTPException(status_code=403, detail="Invalid or Inactive Key. Find your purpose first.")

    try:
        start_time = time.time()
        
        # Groq Call with optimized parameters
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048,
            top_p=1
        )
        
        # Logic Updates
        process_time = round(time.time() - start_time, 3)
        KEY_DATABASE[key]["total_req"] += 1
        
        raw_msg = completion.choices[0].message.content
        
        # --- Ultra Response Formatting ---
        final_msg = f"{raw_msg}\n\ndev: sasuke"

        logger.info(f"Successful chat from {KEY_DATABASE[key]['owner']} using {key}")

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
                    "user_requests": KEY_DATABASE[key]["total_req"],
                    "tier": KEY_DATABASE[key]["tier"]
                }
            }
        )

    except Exception as e:
        logger.error(f"Critical Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "The Susano'o has faltered. Internal server error."}
        )

@app.get("/sasuke@admin", tags=["Admin"])
async def get_dashboard_stats(passkey: str):
    """The Secret Admin Dashboard for PHP integration."""
    if passkey != ADMIN_PASS:
        return JSONResponse(status_code=401, content={"error": "Get out of my sight."})
    
    # Analyze Pool Stats
    total_keys = len(KEY_DATABASE)
    active_keys = sum(1 for k in KEY_DATABASE.values() if k["owner"] is not None)
    
    key_list = []
    for k, v in KEY_DATABASE.items():
        key_list.append({
            "key": k,
            "owner": v["owner"] if v["owner"] else "UNASSIGNED",
            "calls": v["total_req"],
            "tier": v["tier"]
        })

    return {
        "admin": "Sasuke Uchiha",
        "analytics": {
            "total_pool": total_keys,
            "assigned": active_keys,
            "remaining": total_keys - active_keys
        },
        "keys": key_list
    }

@app.get("/reset-key", tags=["Admin"])
async def reset_key_usage(admin_key: str, key_to_reset: str):
    """Resets the usage count of a key."""
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403)
    
    if key_to_reset in KEY_DATABASE:
        KEY_DATABASE[key_to_reset]["total_req"] = 0
        return {"status": "success", "message": f"Usage for {key_to_reset} reset to 0."}
    
    raise HTTPException(status_code=404, detail="Key not found.")

# --- 8. Final Export ---
# Ready for Vercel deployment as 'api/main.py'
