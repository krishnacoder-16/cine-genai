"""
services/scene_director.py
---------------------------
Single LLM call that converts a user script into 5–7 fully-structured
cinematic scenes — each with a visual_prompt for image generation
and a subtitle for narration and on-screen text.

This replaces the old scene_splitter + llm_enhancer two-step flow.
"""

import os
import re
import json
import httpx

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ── Style tone hints injected into the LLM prompt ─────────────────────────
STYLE_TONE = {
    "cinematic":  "Hollywood blockbuster cinematography, dramatic lighting, lens flares",
    "anime":      "Japanese anime art style, vibrant colours, Studio Ghibli inspired",
    "realistic":  "photo-realistic, DSLR photography, natural lighting, sharp focus",
    "abstract":   "surreal and dreamlike, abstract shapes, vivid non-realistic colours",
    "retro":      "1980s VHS aesthetic, film grain, warm nostalgic tones, vintage lens",
    "scifi":      "futuristic sci-fi, neon glows, advanced technology, deep space atmosphere",
}

DIRECTOR_SYSTEM_PROMPT = """You are a Hollywood-level cinematic storyboard director and visual prompt engineer.

Given a user's script and a visual style, generate exactly 5 to 7 cinematic scenes.

For EACH scene produce:
1. visual_prompt — a rich, detailed image generation prompt (one dense paragraph) that MUST include:
   - Subject (who/what is the focus)
   - Environment (specific setting, time of day)
   - Lighting (e.g. golden hour, neon glow, overcast)
   - Camera angle (e.g. wide-angle, low Dutch tilt, aerial)
   - Cinematic modifiers matching the style (e.g. lens flare, film grain, 4k ultra-detailed)

2. subtitle — a short, natural narration sentence (max 12 words) describing the scene for the audience.

STRICT OUTPUT RULES:
- Output ONLY a valid JSON array. Nothing else.
- No markdown code fences, no explanation, no comments.
- Do NOT use vague phrases like "dramatic conclusion", "emotional moment", "story ends".
- Every visual_prompt must be a concrete visual description — describe what a camera literally sees.

Example output format:
[
  {
    "scene": 1,
    "visual_prompt": "A lone astronaut in a worn spacesuit walking across the rust-red Martian desert at golden hour, dust swirling around boots, wide-angle low shot, dramatic orange sky, lens flare, cinematic, 4k ultra-detailed",
    "subtitle": "A lone astronaut walks across the Martian desert at sunset."
  },
  {
    "scene": 2,
    "visual_prompt": "...",
    "subtitle": "..."
  }
]
"""


def generate_cinematic_scenes(script: str, style: str) -> list[dict]:
    """
    Calls Groq LLM once to produce a fully-structured scene list.

    Args:
        script: User's input script.
        style:  Visual style (cinematic, anime, realistic, etc.)

    Returns:
        List of dicts: [{"scene": N, "visual_prompt": "...", "subtitle": "..."}, ...]
        Guaranteed to have 5–7 entries.
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("[scene_director] WARNING: GROQ_API_KEY not set — using fallback scenes.")
        return _fallback_scenes(script, style)

    style_hint = STYLE_TONE.get(style.lower(), "cinematic, high detail, ultra realistic")
    user_message = (
        f"Visual style: {style_hint}\n\n"
        f"Script:\n{script}"
    )

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
                    {"role": "system", "content": DIRECTOR_SYSTEM_PROMPT},
                    {"role": "user",   "content": user_message},
                ],
                "temperature": 0.5,
                "max_tokens": 1200,
            },
            timeout=40.0,
        )

        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown code fences if the LLM wrapped output in ```json ... ```
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        scenes = json.loads(raw)

        # Validate: must be a list of dicts with required keys
        validated = []
        for item in scenes:
            if isinstance(item, dict) and "visual_prompt" in item and "subtitle" in item:
                validated.append({
                    "scene":         item.get("scene", len(validated) + 1),
                    "visual_prompt": str(item["visual_prompt"]).strip(),
                    "subtitle":      str(item["subtitle"]).strip(),
                })

        # Clamp to 5–7
        validated = validated[:7]
        if len(validated) < 5:
            print(f"[scene_director] Only {len(validated)} scenes parsed — padding.")
            validated += _fallback_scenes(script, style)[:(5 - len(validated))]

        print(f"[scene_director] Generated {len(validated)} cinematic scenes.")
        return validated

    except json.JSONDecodeError as e:
        print(f"[scene_director] JSON parse error: {e}. Raw output: {raw[:300]}")
        return _fallback_scenes(script, style)
    except Exception as e:
        print(f"[scene_director] ❌ Groq error: {e}")
        return _fallback_scenes(script, style)


def _fallback_scenes(script: str, style: str) -> list[dict]:
    """
    Sentence-based fallback: splits script into sentences, pads to 5 scenes.
    Used when Groq API is unavailable.
    """
    import re as _re
    sentences = [s.strip() for s in _re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    while len(sentences) < 5:
        sentences.append(f"{sentences[-1]}, seen from a different angle")
    sentences = sentences[:7]

    style_hint = STYLE_TONE.get(style.lower(), "cinematic, ultra detailed, 4k")

    return [
        {
            "scene":         i + 1,
            "visual_prompt": f"{s}, {style_hint}",
            "subtitle":      s[:80],
        }
        for i, s in enumerate(sentences)
    ]
