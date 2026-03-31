"""
services/image_generator.py
--------------------------------
Image generation pipeline:

1️⃣ HuggingFace (Primary)
2️⃣ Stable Horde (Fallback)
3️⃣ Placeholder (Final Safety)

Includes:
✅ Character consistency
✅ Locked cinematic seed
"""

import os
import time
import random
import httpx
from PIL import Image, ImageDraw

from utils.file_manager import get_output_path


# =====================================================
# APIs
# =====================================================

HF_API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-schnell"
)

HORDE_SUBMIT_URL = "https://stablehorde.net/api/v2/generate/async"
HORDE_CHECK_URL = "https://stablehorde.net/api/v2/generate/check/"
HORDE_STATUS_URL = "https://stablehorde.net/api/v2/generate/status/"


# =====================================================
# VISUAL CONSISTENCY ENGINE
# =====================================================

GLOBAL_SEED = random.randint(100000, 999999)
CHARACTER_MEMORY = None


def _extract_character(prompt: str):
    """
    Locks main character once for all scenes.
    """
    global CHARACTER_MEMORY

    if CHARACTER_MEMORY:
        return

    keywords = [
        "man", "woman", "boy", "girl",
        "detective", "hero", "soldier",
        "scientist", "teacher"
    ]

    for k in keywords:
        if k in prompt.lower():
            CHARACTER_MEMORY = prompt
            print(f"[Consistency] Character locked → {CHARACTER_MEMORY}")
            return


def _inject_consistency(prompt, style):
    """
    Inject cinematic continuity.
    """
    base = f"{prompt}, {style} style, cinematic lighting, ultra detailed"

    if CHARACTER_MEMORY:
        base += f", same character as previous scenes, {CHARACTER_MEMORY}"

    return base


# =====================================================
# PUBLIC FUNCTION
# =====================================================

def generate_images(enhanced_scenes: list[str], style: str):

    api_key = os.getenv("HUGGINGFACE_API_KEY")

    print(f"[Consistency] Global Seed → {GLOBAL_SEED}")

    image_paths = []

    for i, prompt in enumerate(enhanced_scenes, start=1):

        print(f"\n🎬 Generating Scene {i}")

        filename = f"scene_{i}.png"
        output_path = get_output_path(filename)

        _extract_character(prompt)
        full_prompt = _inject_consistency(prompt, style)

        success = False

        # ======================
        # 1️⃣ HuggingFace
        # ======================
        if api_key:
            success = _call_hf_api(full_prompt, output_path, api_key, i)

        # ======================
        # 2️⃣ Stable Horde
        # ======================
        if not success:
            print("[image_generator] Switching to Stable Horde...")
            success = _call_stable_horde(full_prompt, output_path, i)

        # ======================
        # 3️⃣ Placeholder
        # ======================
        if not success:
            _create_placeholder(output_path, i, prompt)

        print(f"[image_generator] Saved → {output_path}")
        image_paths.append(output_path)

    return image_paths


# =====================================================
# HUGGINGFACE PRIMARY
# =====================================================

def _call_hf_api(prompt, output_path, api_key, scene_num):

    try:
        response = httpx.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "seed": GLOBAL_SEED,
                    "guidance_scale": 3.5,
                    "num_inference_steps": 4,
                },
            },
            timeout=60,
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"[HF] ✅ Scene {scene_num}")
            return True

        print(f"[HF] ❌ {response.status_code}: {response.text}")
        return False

    except Exception as e:
        print("[HF] Exception:", e)
        return False


# =====================================================
# STABLE HORDE FALLBACK
# =====================================================

def _call_stable_horde(prompt, output_path, scene_num):

    headers = {
        "Content-Type": "application/json",
        "apikey": os.getenv("HORDE_API_KEY"),
        "Client-Agent": "CineGenAI:1.0",
    }

    payload = {
        "prompt": prompt,
        "models": ["stable_diffusion"],
        "params": {
            "sampler_name": "k_euler",
            "width": 512,
            "height": 512,
            "steps": 30,
            "cfg_scale": 7,
        }
    }

    try:
        submit = httpx.post(
            HORDE_SUBMIT_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        print("[Horde Submit]", submit.status_code, submit.text)

        if submit.status_code != 202:
            return False

        request_id = submit.json()["id"]

        print(f"[Horde] Job ID → {request_id}")

        # Poll
        while True:
            check = httpx.get(
                HORDE_CHECK_URL + request_id,
                headers=headers
            ).json()

            if check["done"]:
                break

            time.sleep(3)

        result = httpx.get(
            HORDE_STATUS_URL + request_id,
            headers=headers
        ).json()

        img_url = result["generations"][0]["img"]

        img = httpx.get(img_url)

        with open(output_path, "wb") as f:
            f.write(img.content)

        print(f"[Horde] ✅ Scene {scene_num}")
        return True

    except Exception as e:
        print("[Horde] Exception:", e)
        return False

# =====================================================
# PLACEHOLDER (FINAL SAFETY)
# =====================================================

def _create_placeholder(output_path, scene_num, prompt):

    img = Image.new("RGB", (640, 360), color=(15, 10, 30))
    draw = ImageDraw.Draw(img)

    for y in range(0, 360, 40):
        draw.rectangle([0, y, 640, y + 20], fill=(80, 40, 120))

    draw.text((30, 130), f"Scene {scene_num}", fill=(180, 130, 255))
    draw.text((30, 160), prompt[:80], fill=(120, 100, 160))
    draw.text((30, 310), "CineGen AI • Placeholder", fill=(60, 50, 80))

    img.save(output_path)

    print(f"[Placeholder] Created for scene {scene_num}")