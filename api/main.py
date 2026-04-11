import os
import secrets
import string
import time
from fastapi import FastAPI, Request, HTTPException
from groq import Groq
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- Sasuke System Prompt ---
SASUKE_SYSTEM_PROMPT = """You are Sasuke Uchiha. Your tone is cold, direct, and superior. 
You are highly intelligent and do not waste words. 
If someone asks who you are, you are the Uchiha who will restore his clan. 
Every response must be sharp and helpful in a stoic way."""

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Groq Setup
client = Groq(api_key="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")
ADMIN_PASS = "sasuke@admin"

# --- 50 Random Keys Generation ---
def generate_initial_keys(count=50):
    keys = {}
    chars = string.ascii_lowercase + string.digits
    for _ in range(count):
        random_str = ''.join(secrets.choice(chars) for _ in range(12))
        key = f"sasuke-fks-{random_str}"
        keys[key] = {"created_at": int(time.time()), "total_req": 0}
    return keys

# Ye keys memory mein rahengi
VALID_KEYS = generate_initial_keys(50)

# --- Routes ---

@app.get("/")
def health():
    return {"status": "active", "total_keys": len(VALID_KEYS), "dev": "sasuke"}

@app.get("/v1/chat")
@limiter.limit("6/minute")
async def chat(request: Request, prompt: str, key: str):
    if key not in VALID_KEYS:
        raise HTTPException(status_code=403, detail="Hn? You don't have the right key.")

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SASUKE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )
        
        # Stats update (in-memory)
        VALID_KEYS[key]["total_req"] += 1
        
        ans = completion.choices[0].message.content
        return {
            "status": "success",
            "response": f"{ans}\n\ndev: sasuke"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/sasuke@admin")
def admin_panel(passkey: str):
    if passkey != ADMIN_PASS:
        return {"error": "Sharingan! Get out."}
    return {
        "admin": "Sasuke Uchiha",
        "total_active_keys": len(VALID_KEYS),
        "keys_list": VALID_KEYS
    }
