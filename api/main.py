import os
import secrets
import string
import time
import json
import firebase_admin
from firebase_admin import credentials, db
from fastapi import FastAPI, Request, HTTPException
from groq import Groq
from slowapi import Limiter
from slowapi.util import get_remote_address

# --- Sasuke System Prompt (Directly here to avoid import errors on Vercel) ---
SASUKE_SYSTEM_PROMPT = """You are Sasuke Uchiha. Your tone is cold, direct, and superior. 
You are highly intelligent and do not waste words. 
If someone asks who you are, you are the Uchiha who will restore his clan. 
Every response must be sharp and helpful in a stoic way."""

# --- Firebase Initialization (Safe Mode) ---
fb_initialized = False
try:
    if not firebase_admin._apps:
        fb_json = os.environ.get("FIREBASE_JSON")
        if fb_json:
            # Parse properly even if string is messy
            cred_dict = json.loads(fb_json, strict=False)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://ai-sasukei-apissi-default-rtdb.firebaseio.com"
            })
            fb_initialized = True
except Exception as e:
    print(f"Firebase Init Error: {e}")

# Database Helper function to avoid global 'ref' crashes
def get_db_ref(path="/"):
    if not fb_initialized:
        return None
    return db.reference(path)

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
client = Groq(api_key="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")
ADMIN_PASS = "sasuke@admin"

# --- Helper ---
def generate_sasuke_id():
    chars = string.ascii_lowercase + string.digits
    return "sasuke-fks-" + ''.join(secrets.choice(chars) for _ in range(12))

# --- API Routes ---

@app.get("/")
def health():
    return {"status": "active", "firebase": fb_initialized, "dev": "sasuke"}

@app.get("/gen-key")
def create_key(admin_key: str, user_id: str = "guest"):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    
    ref = get_db_ref("keys")
    if not ref:
        raise HTTPException(status_code=500, detail="Database not connected.")
        
    new_k = generate_sasuke_id()
    ref.child(new_k).set({
        "owner": user_id,
        "created_at": int(time.time()),
        "total_req": 0,
        "last_used": int(time.time()),
        "status": "active"
    })
    return {"status": "success", "api_key": new_k}

@app.get("/v1/chat")
@limiter.limit("6/minute")
async def chat(request: Request, prompt: str, key: str):
    ref = get_db_ref("keys")
    if not ref:
        raise HTTPException(status_code=500, detail="Database connection lost.")

    key_data = ref.child(key).get()
    if not key_data:
        raise HTTPException(status_code=403, detail="Invalid Key.")

    # 30 Days Expiry
    if (time.time() - key_data.get('last_used', 0)) > (30 * 86400):
        ref.child(key).delete()
        raise HTTPException(status_code=403, detail="Key expired.")

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SASUKE_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}]
        )
        
        # Updates
        ref.child(key).update({
            "total_req": key_data.get('total_req', 0) + 1,
            "last_used": int(time.time())
        })
        
        return {"status": "success", "response": f"{completion.choices[0].message.content}\n\ndev: sasuke"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/sasuke@admin")
def admin_panel(passkey: str):
    if passkey != ADMIN_PASS:
        return {"error": "Unauthorized"}
    ref = get_db_ref("/")
    return ref.get() if ref else {"error": "No DB"}
