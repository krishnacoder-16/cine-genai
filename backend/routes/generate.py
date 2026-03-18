"""
routes/generate.py
-------------------
Defines the POST /generate-video endpoint.

New pipeline using scene_director (replaces scene_splitter + llm_enhancer):
  1. scene_director  → 5–7 scenes with visual_prompt + subtitle each
  2. image_generator → one AI image per visual_prompt
  3. voice_generator → narration audio from joined subtitles
  4. video_creator   → cinematic video with audio + subtitle overlays
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.scene_director  import generate_cinematic_scenes
from services.image_generator import generate_images
from services.voice_generator import generate_voice
from services.video_creator   import create_video

# ── Router ───────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="",
    tags=["Generate"],
)


# ── Request model ─────────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    script: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The video script or scene description",
        example="A lone astronaut walks across Mars at sunset. A dust storm rises on the horizon.",
    )
    style: str = Field(
        ...,
        description="Visual style identifier (e.g. cinematic, anime, realistic)",
        example="cinematic",
    )


# ── Response model ────────────────────────────────────────────────────────────
class GenerateResponse(BaseModel):
    success:   bool
    video_url: str
    message:   str


# ── POST /generate-video ──────────────────────────────────────────────────────
@router.post(
    "/generate-video",
    response_model=GenerateResponse,
    summary="Generate a cinematic video from a script",
)
async def generate_video(request: GenerateRequest):
    """
    Full AI video generation pipeline.

    Step 1 — scene_director:
        Single LLM call → 5–7 scenes, each with:
          • visual_prompt  (rich prompt for image generation)
          • subtitle       (short narration line)

    Step 2 — image_generator:
        Calls HuggingFace FLUX for each visual_prompt → scene_N.png

    Step 3 — voice_generator:
        Joins all subtitles → TTS narration.mp3 (synced to scenes)

    Step 4 — video_creator:
        Assembles cinematic slideshow — Ken Burns zoom, crossfade
        transitions, subtitle overlays, narration audio.
    """
    try:
        # ── Step 1: Generate structured scenes via LLM ────────────────────
        scenes = generate_cinematic_scenes(request.script, request.style)
        # scenes is: [{"scene": N, "visual_prompt": "...", "subtitle": "..."}, ...]

        visual_prompts = [s["visual_prompt"] for s in scenes]
        subtitles      = [s["subtitle"]      for s in scenes]

        print(f"[generate] {len(scenes)} scenes ready.")

        # ── Step 2: Generate one image per visual prompt ──────────────────
        image_paths = generate_images(visual_prompts, request.style)

        # ── Step 3: Generate narration from subtitles (not raw script) ────
        # Using subtitles keeps narration tightly synced with what's on screen
        narration_script = " ".join(subtitles)
        audio_path       = generate_voice(narration_script)

        # ── Step 4: Assemble final cinematic video ────────────────────────
        video_url = create_video(
            image_paths  = image_paths,
            style        = request.style,
            audio_path   = audio_path,
            scene_texts  = subtitles,    # subtitle per scene overlay
        )

        return GenerateResponse(
            success   = True,
            video_url = video_url,
            message   = f"Video generated successfully with {len(scenes)} scenes!",
        )

    except Exception as e:
        print(f"[generate] ❌ Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
