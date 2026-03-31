"""
services/image_generator.py
-----------------------------
Image generation with automatic failover:

1. HuggingFace (Primary)
2. Stable Horde (Fallback)
3. Placeholder (Final safety)

Setup:
  HUGGINGFACE_API_KEY=hf_xxx
"""

import os
import time
import httpx
from PIL import Image, ImageDraw

from utils.file_manager import get_output_path


# ===============================
# APIs
# ===============================

HF_API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-schnell"
)

HORDE_SUBMIT_URL = "https://stablehorde.net/api/v2/generate/async"
HORDE_CHECK_URL = "https://stablehorde.net/api/v2/generate/check/"
HORDE_STATUS_URL = "https://stablehorde.net/api/v2/generate/status/"


# ===============================
# PUBLIC FUNCTION
# ===============================

def generate_images(enhanced_scenes: list[str], style: str) -> list[str]:

    api_key = os.getenv("HUGGINGFACE_API_KEY")

    if not api_key:
        print("[image_generator] WARNING: HF key missing.")

    image_paths = []

    for i, prompt in enumerate(enhanced_scenes, start=1):

        print(f"[image_generator] Generating image for scene {i}")

        filename = f"scene_{i}.png"
        output_path = get_output_path(filename)

        success = False

        # -------------------------
        # 1️⃣ HuggingFace
        # -------------------------
        if api_key:
            success = _call_hf_api(prompt, style, output_path, api_key, i)

        # -------------------------
        # 2️⃣ Stable Horde fallback
        # -------------------------
        if not success:
            print("[image_generator] Switching to Stable Horde...")
            success = _call_stable_horde(prompt, style, output_path, i)

        # -------------------------
        # 3️⃣ Local SD fallback
        # -------------------------
        if not success:
            print("[image_generator] Switching to Local Stable Diffusion...")
            success = _call_local_sd(prompt, style, output_path, i)

        # -------------------------
        # 4 Placeholder fallback
        # -------------------------
        if not success:
            _create_placeholder(output_path, i, prompt)

        print(f"[image_generator] Saved → {output_path}")
        image_paths.append(output_path)

    return image_paths


# ===============================
# HUGGINGFACE
# ===============================

def _call_hf_api(prompt, style, output_path, api_key, scene_num):

    full_prompt = f"{prompt}, {style} style, cinematic lighting, ultra detailed, 4k"

    try:
        response = httpx.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"inputs": full_prompt},
            timeout=60,
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"[HF] ✅ Scene {scene_num} generated")
            return True

        print(f"[HF] ❌ Error {response.status_code}: {response.text}")
        return False

    except Exception as e:
        print(f"[HF] ❌ Exception: {e}")
        return False


# ===============================
# STABLE HORDE FALLBACK
# ===============================

def _call_stable_horde(prompt, style, output_path, scene_num):

    full_prompt = f"{prompt}, {style} style, cinematic lighting, film still, ultra detailed"

    headers = {
        "Content-Type": "application/json",
        "Client-Agent": "CineGenAI:1.0:AravGupta",
        "apikey":os.getenv("HORDE_API_KEY"),   # anonymous free usage
    }

    try:
        # STEP 1 — Submit job
        submit = httpx.post(
            HORDE_SUBMIT_URL,
            headers=headers,
            json={
                "prompt": full_prompt,
                "params": {
                    "width": 512,
                    "height": 512,
                    "steps": 30,
                    "cfg_scale": 7
                }
            },
            timeout=30,
        )

        print("[Horde] Submit response:", submit.status_code, submit.text)

        if submit.status_code != 202:
            return False

        request_id = submit.json()["id"]

        print(f"[Horde] Job ID → {request_id}")

        # STEP 2 — Poll generation
        while True:
            check = httpx.get(
                HORDE_CHECK_URL + request_id,
                headers=headers
            ).json()

            if check["done"]:
                break

            time.sleep(3)

        # STEP 3 — Fetch result
        result = httpx.get(
            HORDE_STATUS_URL + request_id,
            headers=headers
        ).json()

        image_url = result["generations"][0]["img"]

        # STEP 4 — Download image
        img = httpx.get(image_url)

        with open(output_path, "wb") as f:
            f.write(img.content)

        print(f"[Horde] ✅ Scene {scene_num} generated")
        return True

    except Exception as e:
        print("[Horde] Exception:", e)
        return False

# ===============================
# Local Stable Diffusion
# ===============================

def _call_local_sd(prompt, style, output_path, scene_num):

    try:
        print("[Local SD] Attempting local generation...")

        from diffusers import StableDiffusionPipeline
        import torch

        model_id = "runwayml/stable-diffusion-v1-5"

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32
        )

        pipe = pipe.to("cpu")   # works without GPU

        full_prompt = f"{prompt}, {style} style, cinematic lighting"

        image = pipe(full_prompt).images[0]
        image.save(output_path)

        print(f"[Local SD] ✅ Scene {scene_num} generated locally")
        return True

    except Exception as e:
        print("[Local SD] ❌ Failed:", e)
        return False

# ===============================
# PLACEHOLDER (FINAL SAFETY)
# ===============================

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