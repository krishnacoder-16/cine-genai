"""
main.py
-------
Entry point for the CineGen AI FastAPI backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from routes.generate import router as generate_router

load_dotenv()

# ── Create the FastAPI app ──────────────────────────────────────────────────
app = FastAPI(
    title="CineGen AI API",
    description="Backend API for AI-powered video generation.",
    version="0.1.0",
)

# ── CORS — must be added BEFORE mounting static files ──────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Cache-Control", "X-Accel-Buffering"],
)

# ── Register route modules ──────────────────────────────────────────────────
# Provides: POST /generate, GET /progress/{job_id}
app.include_router(generate_router)

# ── Static files — serve generated outputs at /outputs/<filename> ──────────
# Mounted AFTER routes so CORS middleware applies to everything
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# ── Health check ────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "CineGen AI backend is running 🎬"}
