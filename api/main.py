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
from .prompts import SASUKE_SYSTEM_PROMPT

# --- Firebase Init ---
if not firebase_admin._apps:
    fb_json = os.environ.get("FIREBASE_JSON")
    if fb_json:
        cred = credentials.Certificate(json.loads(fb_json))
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://ai-sasukei-apissi-default-rtdb.firebaseio.com"
        })

ref = db.reference("/")
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)

client = Groq(api_key="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")
ADMIN_PASS = "sasuke@admin" # Ye password tumhari PHP file mein secret rahega

# --- Helper ---
def generate_sasuke_id():
    chars = string.ascii_lowercase + string.digits
    return "sasuke-fks-" + ''.join(secrets.choice(chars) for _ in range(12))

# --- API Routes ---

@app.get("/gen-key")
def create_key(admin_key: str, user_id: str = "guest"):
    # Sirf tumhara PHP server hi ye call kar payega
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    
    new_k = generate_sasuke_id()
    ref.child("keys").child(new_k).set({
        "owner": user_id, # PHP se user_id bhej dena
        "created_at": int(time.time()),
        "total_req": 0,
        "last_used": int(time.time()),
        "status": "active"
    })
    return {"status": "success", "api_key": new_k}

@app.get("/del-key")
def delete_key(admin_key: str, key: str):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Unauthorized.")
    
    if ref.child("keys").child(key).get():
        ref.child("keys").child(key).delete()
        return {"status": "success", "message": "Key destroyed."}
    raise HTTPException(status_code=404, detail="Key not found.")

@app.get("/v1/chat")
@limiter.limit("6/minute")
async def chat(request: Request, prompt: str, key: str):
    key_data = ref.child("keys").child(key).get()
    
    if not key_data:
        raise HTTPException(status_code=403, detail="Invalid Key.")

    # 30 Days Expiry
    if (time.time() - key_data.get('last_used', 0)) > (30 * 86400):
        ref.child("keys").child(key).delete()
        raise HTTPException(status_code=403, detail="Key expired.")

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SASUKE_SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}]
        )
        
        # Updates
        ref.child("keys").child(key).update({
            "total_req": key_data.get('total_req', 0) + 1,
            "last_used": int(time.time())
        })
        
        return {"status": "success", "response": f"{completion.choices[0].message.content}\n\ndev: sasuke"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
