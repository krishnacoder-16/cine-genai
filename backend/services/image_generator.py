"""
services/image_generator.py
-----------------------------
Generates one image per enhanced scene prompt using the
HuggingFace Inference API (Stable Diffusion XL).

Setup:
  Add to backend/.env:
    HUGGINGFACE_API_KEY=hf_your_key_here

  Get your free key at: https://huggingface.co/settings/tokens

Fallback:
  If the API key is missing or the call fails, a solid-color placeholder
  image is created with Pillow so the rest of the pipeline keeps running.
"""

import os
import httpx
from PIL import Image, ImageDraw, ImageFont

from utils.file_manager import get_output_path

# FLUX.1-schnell: HuggingFace's recommended free text-to-image model on the router
HF_API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-schnell"
)


def generate_images(enhanced_scenes: list[str], style: str) -> list[str]:
    """
    Generates one image per scene and saves to backend/outputs/.

    Args:
        enhanced_scenes: Enriched visual prompts from llm_enhancer.
        style:           Visual style (used for extra prompt context).

    Returns:
        List of absolute file paths to the saved images.
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")

    if not api_key:
        print("[image_generator] WARNING: HUGGINGFACE_API_KEY not set — using placeholders.")

    image_paths = []

    for i, prompt in enumerate(enhanced_scenes, start=1):
        print(f"[image_generator] Generating image for scene {i}...")

        filename    = f"scene_{i}.png"
        output_path = get_output_path(filename)

        success = False

        # ── Try HuggingFace API ────────────────────────────────────────────
        if api_key:
            success = _call_hf_api(prompt, style, output_path, api_key, i)

        # ── Fallback: solid-colour placeholder with Pillow ─────────────────
        if not success:
            _create_placeholder(output_path, i, prompt)

        print(f"[image_generator] Saved image → {output_path}")
        image_paths.append(output_path)

    return image_paths


# ── Private helpers ────────────────────────────────────────────────────────

def _call_hf_api(
    prompt: str,
    style: str,
    output_path: str,
    api_key: str,
    scene_num: int,
) -> bool:
    """Calls the HuggingFace Inference API and saves the returned image."""
    # Enrich prompt with style for even better results
    full_prompt = f"{prompt}, {style} style, highly detailed, 4k, professional"

    try:
        response = httpx.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"inputs": full_prompt},
            timeout=60.0,   # HF cold-start can take up to ~30s on free tier
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"[image_generator] ✅ Scene {scene_num} image generated via HuggingFace.")
            return True

        # 503 = model still loading (common on HF free tier cold-start)
        if response.status_code == 503:
            print(f"[image_generator] ⚠️  Model loading (503). Try again in ~30s.")
        else:
            # Print full body so we can see the exact error message
            print(
                f"[image_generator] ❌ HF API error {response.status_code}: "
                f"{response.text}"
            )
        return False

    except Exception as e:
        print(f"[image_generator] ❌ Request failed: {e}")
        return False


def _create_placeholder(output_path: str, scene_num: int, prompt: str) -> None:
    """Creates a simple dark-themed placeholder image using Pillow."""
    # Dark purple background matching the CineGen brand
    img  = Image.new("RGB", (640, 360), color=(15, 10, 30))
    draw = ImageDraw.Draw(img)

    # Gradient-ish overlay bars for visual interest
    for y in range(0, 360, 40):
        alpha = int(255 * (1 - y / 360) * 0.15)
        draw.rectangle([0, y, 640, y + 20], fill=(80, 40, 120))

    # Scene label
    draw.text((30, 130), f"Scene {scene_num}", fill=(180, 130, 255))
    draw.text((30, 160), prompt[:80] + ("…" if len(prompt) > 80 else ""), fill=(120, 100, 160))
    draw.text((30, 310), "CineGen AI  •  Placeholder", fill=(60, 50, 80))

    img.save(output_path)
    print(f"[image_generator] 🖼️  Placeholder created for scene {scene_num}.")
