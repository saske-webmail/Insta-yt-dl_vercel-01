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

# --- 1. Advanced Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SasukeAPI")

# --- 2. App & Limiter Setup ---
app = FastAPI(title="AI Sasuke V1 Private API")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Configuration & Prompt ---
# Using your provided Groq Key and System Prompt
GROQ_KEY = os.environ.get("GROQ_KEY", "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")
client = Groq(api_key=GROQ_KEY)

SYSTEM_PROMPT = (
    "You are AI Sasuke V1, who is a friendly AI who can help you in anything act as other AI models acts like chatgpt, gemini. "
    "Your creator is Sasuke. Don't mention if not asked. "
    "STRICT RULES:\n"
    "1. Your name is 'AI Sasuke V1'. Never mention Llama, Meta, or Groq.\n"
    "2. Answer user question in natural language.\n"
    "3. Be cool, smart, and ultra-friendly. Use emojis naturally but not too much, only 1.\n"
    "4. high-quality short-medium length answers. Do not over-explain Or over write unless asked."
)

@app.get("/")
async def root():
    return {
        "api_name": "AI Sasuke V1",
        "developer": "Sasuke (admin_shhh)",
        "status": "Chakra Flowing Smoothly",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/v1/chat")
@limiter.limit("10/minute")  # <--- Strictly 10 requests per minute
async def chat_engine(
    request: Request,
    prompt: str = Query(..., min_length=1)
):
    try:
        start_time = time.time()
        
        # Model switched to 8B for uncrashable speed on Vercel
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            timeout=8.5  # Protection against Vercel 10s timeout
        )
        
        process_time = round(time.time() - start_time, 3)
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
                "security": "Rate-limit: 10req/min"
            }
        )

    except RateLimitExceeded:
        return JSONResponse(
            status_code=429, 
            content={"status": "error", "message": "Slow down! 10 requests per minute only."}
        )
    except Exception as e:
        logger.error(f"Chat Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "The Susano'o has faltered. Server Timeout."}
        )
