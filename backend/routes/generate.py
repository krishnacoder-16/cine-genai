import asyncio
import uuid
import base64
import pathlib
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from utils.progress_manager import (
    create_job,
    event_stream,
    send_event,
)

from services.scene_director import generate_cinematic_scenes
from services.image_generator import generate_images
from services.voice_generator import generate_voice
from services.video_creator import create_video

router = APIRouter()


class GenerateRequest(BaseModel):
    script: str
    style: str = "Cinematic"


@router.post("/generate")
async def start_generation(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    create_job(job_id)
    background_tasks.add_task(_run_pipeline, job_id, req.script, req.style)
    return {"job_id": job_id}


@router.get("/progress/{job_id}")
async def progress_stream(job_id: str):
    return StreamingResponse(
        event_stream(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _run_pipeline(job_id: str, script: str, style: str):
    try:
        # Step 1: Analyse script
        await send_event(job_id, "status", {
            "stage": "analysing",
            "message": "Analysing script and splitting into scenes\u2026",
            "progress": 5,
        })

        scenes = await asyncio.to_thread(generate_cinematic_scenes, script, style)
        total_scenes = len(scenes)

        await send_event(job_id, "scenes_ready", {
            "total": total_scenes,
            "scenes": [{"subtitle": s["subtitle"]} for s in scenes],
            "progress": 10,
        })

        # Step 2: Generate images
        # generate_images(enhanced_scenes: list[str], style: str) -> list[str]
        await send_event(job_id, "status", {
            "stage": "images",
            "message": f"Generating {total_scenes} scene images\u2026",
            "progress": 12,
        })

        visual_prompts = [s["visual_prompt"] for s in scenes]
        image_paths = await asyncio.to_thread(generate_images, visual_prompts, style)

        for i, (img_path, scene) in enumerate(zip(image_paths, scenes)):
            img_b64 = ""
            try:
                img_b64 = base64.b64encode(pathlib.Path(img_path).read_bytes()).decode()
            except Exception:
                pass

            progress = 12 + int(((i + 1) / total_scenes) * 55)
            await send_event(job_id, "scene_image", {
                "index": i,
                "subtitle": scene["subtitle"],
                "image_b64": img_b64,
                "progress": progress,
                "message": f"Scene {i + 1}/{total_scenes} image ready",
            })

        # Step 3: Generate voiceover
        # generate_voice(script: str) -> str
        await send_event(job_id, "status", {
            "stage": "voice",
            "message": "Generating voiceover narration\u2026",
            "progress": 70,
        })

        subtitles = [s["subtitle"] for s in scenes]
        audio_path = await asyncio.to_thread(generate_voice, " ".join(subtitles))

        await send_event(job_id, "status", {
            "stage": "voice",
            "message": "Voiceover ready",
            "progress": 78,
        })

        # Step 4: Assemble video
        # create_video(image_paths, audio_path, subtitles, ...) -> str
        await send_event(job_id, "status", {
            "stage": "assembling",
            "message": "Assembling final video with cinematic effects\u2026",
            "progress": 80,
        })

        video_path = await asyncio.to_thread(
            create_video, image_paths, style, audio_path, subtitles
        )

        # Step 5: Done
        filename = pathlib.Path(video_path).name
        download_url = f"/outputs/{filename}"

        await send_event(job_id, "complete", {
            "stage": "complete",
            "message": "Your video is ready!",
            "progress": 100,
            "download_url": download_url,
        })

    except Exception as exc:
        await send_event(job_id, "error", {
            "stage": "error",
            "message": f"Generation failed: {str(exc)}",
            "progress": 0,
        })
