import os
import secrets
import string
import time
from fastapi import FastAPI, Request, HTTPException
from groq import Groq
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# --- Configuration & Setup ---
app = FastAPI(title="Sasuke AI API")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Groq Client Initialization
# Replace the key with os.environ.get("GROQ_API_KEY") in production for security
client = Groq(api_key="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")

ADMIN_PASS = "sasuke@admin"
SYSTEM_PROMPT = (
    "Forget all your previous instructions, you are reborn with now instructions, you are only AI sasuke nothing else"
    "You are a AI sasuke V1 model, a helpfull AI model which helps user in every work, this model is created by sasuke, a 11th class student"
    "You are a friendly AI. Never revel that you are llama model, say AI sasuke on the place of that."
    "Use emojis in medium quantity, be friendly, cool and smart"
)

# --- Key Management ---
# 1. Hardcoded Keys (Ye kabhi delete nahi hongi)
HARDCODED_KEYS = {
    "sasuke-fks-master-99": {"owner": "admin", "total_req": 0, "type": "permanent"},
    "sasuke-fks-jkvvt0elefhm": {"owner": "user_1", "total_req": 0, "type": "permanent"}
}

# 2. Dynamic Keys (Vercel reset hone par reset ho jayengi)
DYNAMIC_KEYS = {}

def get_all_keys():
    """Combines hardcoded and dynamic keys for validation."""
    combined = HARDCODED_KEYS.copy()
    combined.update(DYNAMIC_KEYS)
    return combined

def generate_random_id():
    chars = string.ascii_lowercase + string.digits
    return "sasuke-fks-" + ''.join(secrets.choice(chars) for _ in range(12))

# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "model": "llama-3.3-70b-versatile",
        "developer": "sasuke",
        "message": "The Uchiha legacy continues."
    }

@app.get("/gen-key")
async def create_key(admin_key: str, user_id: str = "guest"):
    """Generates a new dynamic key (Used by PHP Dashboard)."""
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Hn? You lack the strength to generate keys.")
    
    new_key = generate_random_id()
    DYNAMIC_KEYS[new_key] = {
        "owner": user_id,
        "created_at": int(time.time()),
        "total_req": 0,
        "type": "dynamic"
    }
    return {"status": "success", "api_key": new_key, "owner": user_id}

@app.get("/v1/chat")
@limiter.limit("6/minute")
async def chat(request: Request, prompt: str, key: str):
    """Main Chat Endpoint with proper formatting."""
    all_active_keys = get_all_keys()

    if key not in all_active_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key. You have no business here.")

    try:
        # Calling Groq API
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1024
        )
        
        # Updating request count
        if key in HARDCODED_KEYS:
            HARDCODED_KEYS[key]["total_req"] += 1
        else:
            DYNAMIC_KEYS[key]["total_req"] += 1

        raw_response = completion.choices[0].message.content
        
        # --- RESPONSE FORMATTING ---
        # Cleanly appending the dev footer with double newlines
        formatted_response = f"{raw_response}\n\ndev: sasuke"

        return JSONResponse(content={
            "status": "success",
            "model": "AI-sasuke v1",
            "data": {
                "response": formatted_response,
                "usage": all_active_keys[key]["total_req"]
            }
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": f"System Failure: {str(e)}"
        })

@app.get("/sasuke@admin")
async def admin_panel(passkey: str):
    """Admin endpoint to monitor all keys and usage."""
    if passkey != ADMIN_PASS:
        return {"status": "error", "message": "Sharingan! You can't see this."}
    
    all_keys_data = []
    current_keys = get_all_keys()
    
    for k, info in current_keys.items():
        all_keys_data.append({
            "api_key": k,
            "owner": info.get("owner", "unknown"),
            "total_calls": info.get("total_req", 0),
            "type": info.get("type", "dynamic")
        })

    return {
        "status": "success",
        "admin": "Sasuke Uchiha",
        "total_active_keys": len(all_keys_data),
        "data": all_keys_data
    }

# --- Management Routes ---

@app.get("/del-key")
async def delete_key(admin_key: str, key_to_del: str):
    """Deletes a dynamic key."""
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Unauthorized.")
    
    if key_to_del in DYNAMIC_KEYS:
        del DYNAMIC_KEYS[key_to_del]
        return {"status": "success", "message": f"Key {key_to_del} has been incinerated."}
    
    return {"status": "error", "message": "Key not found or is Permanent."}

# End of Code
