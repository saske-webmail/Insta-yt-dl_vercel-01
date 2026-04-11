import os
import secrets
import string
from fastapi import FastAPI, Request, HTTPException
from groq import Groq
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate Limiter setup (6 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Groq API Key
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

# Temporary In-memory Key Store
# Note: Vercel reset hone par ye khali ho jayega. 
# Ek default key daal raha hoon testing ke liye.
valid_keys = {"sasuke-fks(master99)"}

SYSTEM_PROMPT = """You are Sasuke Uchiha. Your tone is cold, direct, and superior. 
You are highly intelligent and do not waste words. 
If someone asks who you are, you are the Uchiha who will restore his clan. 
Every response must be sharp and helpful in a stoic way."""

# --- ROUTES ---

@app.get("/")
def home():
    return {"status": "active", "dev": "sasuke", "message": "Sasuke AI API is running."}

@app.get("/gen-key")
def generate_key():
    # Sasuke-fks(random8chars) format
    random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    new_key = f"sasuke-fks({random_part})"
    valid_keys.add(new_key)
    return {"status": "success", "api_key": new_key}

@app.get("/del-key")
def delete_key(key: str):
    if key in valid_keys:
        valid_keys.remove(key)
        return {"status": "success", "message": f"Key {key} has been destroyed."}
    return {"status": "error", "message": "Key not found."}

@app.get("/v1/chat")
@limiter.limit("6/minute")
async def chat(request: Request, prompt: str, key: str):
    # Key validation
    if key not in valid_keys:
        raise HTTPException(status_code=403, detail="Hn? You don't have the right key.")

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        response_text = completion.choices[0].message.content
        
        # Adding the mandatory footer
        return {
            "status": "success",
            "response": f"{response_text}\n\ndev: sasuke"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
