"""
main.py
-------
Entry point for the CineGen AI FastAPI backend.

What this file does:
  1. Creates the FastAPI app instance
  2. Configures CORS so the Next.js frontend (localhost:3000) can call this API
  3. Registers the /generate-video route from routes/generate.py
  4. Adds a simple health-check endpoint at GET /

To run the server:
    uvicorn main:app --reload --port 8000

Then visit:
    http://localhost:8000        → health check
    http://localhost:8000/docs  → interactive Swagger UI (auto-generated!)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load .env file so os.getenv("GROQ_API_KEY") works without manually
# setting the variable in PowerShell every time.
load_dotenv()

from routes.generate import router as generate_router

# ── Create the FastAPI app ──────────────────────────────────────────────────
app = FastAPI(
    title="CineGen AI API",
    description="Backend API for AI-powered video generation.",
    version="0.1.0",
)

# ── Static files — serve generated outputs at /outputs/<filename> ──────────
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# ── CORS — allow the Next.js frontend to call this API ─────────────────────
# During development we allow localhost:3000.
# In production, replace with your actual deployed frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# ── Register route modules ──────────────────────────────────────────────────
# All /generate-video endpoints are defined in routes/generate.py
app.include_router(generate_router)


# ── Health check ────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    """Simple ping to verify the server is running."""
    return {"status": "ok", "message": "CineGen AI backend is running 🎬"}
