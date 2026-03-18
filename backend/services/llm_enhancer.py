"""
services/llm_enhancer.py
-------------------------
Uses httpx to call the Groq REST API directly (no SDK).
Groq's API is OpenAI-compatible: POST to /openai/v1/chat/completions.

Why no SDK: groq SDK 1.0.0 passes `proxies` to httpx internally,
which httpx 0.28+ removed. Direct REST call avoids the conflict entirely.
"""

import os
import httpx

# ── Style-specific tone instructions ──────────────────────────────────────
STYLE_TONE = {
    "cinematic":  "Hollywood blockbuster cinematography with dramatic lighting and lens flares",
    "anime":      "Japanese anime art style, vibrant colours, expressive characters, Studio Ghibli inspired",
    "realistic":  "photo-realistic, DSLR photography, natural lighting, sharp focus",
    "abstract":   "surreal and dreamlike, abstract shapes, vibrant non-realistic colours",
    "retro":      "1980s VHS aesthetic, film grain, warm nostalgic colours, vintage lens",
    "scifi":      "futuristic sci-fi, neon glows, advanced technology, deep space atmosphere",
}

SYSTEM_PROMPT = """You are a professional visual prompt engineer for AI image generation (Stable Diffusion / FLUX).

Your task: Transform the scene description into ONE single dense image-generation prompt.

The prompt MUST include ALL of these elements:
  1. Subject — who or what is the main focus
  2. Environment — specific setting, location, time of day
  3. Lighting — e.g. golden hour, rim lighting, neon glow, overcast
  4. Camera angle — e.g. wide-angle, low-angle Dutch tilt, close-up, aerial
  5. Cinematic detail — e.g. lens flare, depth of field, film grain, 4k ultra-detailed

Rules:
  - Output ONLY the final prompt as one paragraph. No labels. No explanation.
  - Never write vague phrases like "dramatic conclusion", "end of story", or "emotional moment".
  - Be specific and visual. Describe what a camera would literally see.
  - Adapt style modifiers to match the provided visual style.
"""


def enhance_prompt(scene: str, style: str) -> str:
    """
    Sends a scene to Groq (llama3-8b-8192) and returns an enhanced prompt.
    Falls back gracefully if the key is missing or API errors occur.
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("[llm_enhancer] WARNING: GROQ_API_KEY not set. Using fallback.")
        return f"{scene}, cinematic lighting, ultra detailed, 4k"

    style_instruction = STYLE_TONE.get(style.lower(), "cinematic lighting, high detail")

    # Build the exact payload the Groq API expects
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Visual style: {style_instruction}\n\n"
                    f"Scene: {scene}"
                )
            }
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = httpx.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30.0
        )

        # Print full raw response for debugging
        print(f"\n[llm_enhancer] HTTP Status: {response.status_code}")
        print(f"[llm_enhancer] Raw response: {response.text[:500]}\n")

        response.raise_for_status()

        data = response.json()
        enhanced = data["choices"][0]["message"]["content"].strip()

        print(f"[llm_enhancer] ✅ Enhanced prompt (style={style}):")
        print(f"  IN : {scene[:80]}")
        print(f"  OUT: {enhanced[:120]}\n")

        return enhanced

    except httpx.HTTPStatusError as e:
        print(f"[llm_enhancer] ❌ HTTP {e.response.status_code}: {e.response.text[:300]}")
        return f"{scene}, cinematic lighting, ultra detailed, 4k"

    except Exception as e:
        print(f"[llm_enhancer] ❌ Error: {e}")
        return f"{scene}, cinematic lighting, ultra detailed, 4k"


def enhance_scenes(scenes: list[str], style: str) -> list[str]:
    """Loops over scenes and enhances each one. Called by routes/generate.py."""
    enhanced = []
    for i, scene in enumerate(scenes):
        print(f"[llm_enhancer] Enhancing scene {i + 1}/{len(scenes)}…")
        enhanced.append(enhance_prompt(scene, style))
    return enhanced
