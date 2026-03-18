"""
services/scene_splitter.py
---------------------------
Uses Groq LLM to intelligently split a user script into 5-7 specific,
visual scene descriptions — one per image to be generated.

Falls back to a sentence-based splitter if the API key is missing.
"""

import os
import re
import httpx

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SPLITTER_SYSTEM_PROMPT = """You are a professional video storyboard artist.

Your task:
- Read the user's script.
- Break it into exactly 5 to 7 individual visual scene descriptions.
- Each scene must describe ONE visual moment: subject, environment, action, mood.
- Each scene must be a concrete, specific image prompt — NOT a narrative sentence.
- Do NOT write "Scene 1:", numbers, or any labels.
- Output ONLY the scenes as a plain numbered list (one per line), like:
  1. An astronaut walking across the red Martian desert at sunset
  2. Dust swirling around the astronaut's boots
  3. ...

Rules:
- Minimum 5 scenes, maximum 7.
- No vague scenes like "dramatic conclusion" or "story ending".
- Every scene must contain a clear subject + setting + visual detail.
"""


def split_into_scenes(script: str) -> list[str]:
    """
    Splits the user script into 5–7 concrete visual scene descriptions.

    Args:
        script: Full user-entered script.

    Returns:
        List of visual scene description strings (no 'Scene X:' prefix).
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("[scene_splitter] WARNING: GROQ_API_KEY not set — using sentence fallback.")
        return _sentence_fallback(script)

    try:
        response = httpx.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": SPLITTER_SYSTEM_PROMPT},
                    {"role": "user",   "content": f"Script:\n{script}"},
                ],
                "temperature": 0.4,   # low temp = more consistent structured output
                "max_tokens": 600,
            },
            timeout=30.0,
        )

        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()

        # Parse the numbered list output: "1. description\n2. description\n..."
        scenes = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            # Strip leading numbers + punctuation: "1.", "1)", "1 -", etc.
            cleaned = re.sub(r"^\d+[\.\)\-]\s*", "", line).strip()
            if cleaned:
                scenes.append(cleaned)

        # Clamp to 5–7
        scenes = scenes[:7]

        if len(scenes) < 5:
            print(f"[scene_splitter] Only {len(scenes)} scenes from LLM — padding with fallback.")
            scenes += _sentence_fallback(script)[:(5 - len(scenes))]

        print(f"[scene_splitter] Generated {len(scenes)} scenes.")
        return scenes

    except Exception as e:
        print(f"[scene_splitter] ❌ Groq error: {e}. Using sentence fallback.")
        return _sentence_fallback(script)


def _sentence_fallback(script: str) -> list[str]:
    """
    Splits by sentence boundaries and produces 5 scenes as a fallback.
    Each sentence becomes one visual scene, padded if needed.
    """
    # Split on period / exclamation / question followed by a space or end
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]

    # Ensure at least 5 items by repeating/varying if script is too short
    while len(sentences) < 5:
        sentences.append(f"{sentences[-1]}, viewed from another angle")

    return sentences[:7]
