"""
services/video_creator.py
--------------------------
Creates a professional cinematic video from AI-generated images.

Features:
  - Duration of each scene synced to narration audio
  - Ken Burns slow zoom per image (100% → 105%)
  - CrossFade transitions between scenes
  - Pillow-based subtitles pinned to the bottom (no ImageMagick)
  - Narration audio + optional background music at 15%

Final output: outputs/final_video.mp4
"""

import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
)
from moviepy.video.fx import CrossFadeIn

from utils.file_manager import get_output_path

# ── Config ──────────────────────────────────────────────────────────────────
VIDEO_W, VIDEO_H   = 1280, 720        # HD resolution for better quality
VIDEO_SIZE         = (VIDEO_W, VIDEO_H)
DEFAULT_DURATION   = 4.0              # seconds per scene when no narration
CROSSFADE_SECS     = 0.5
BG_MUSIC_VOL       = 0.15
FINAL_FILENAME     = "final_video.mp4"
SUBTITLE_H         = 52      # height of subtitle bar in pixels
SUBTITLE_MARGIN    = 10      # gap from the bottom edge


def create_video(
    image_paths: list[str],
    style: str,
    audio_path: str = None,
    scene_texts: list[str] = None,
) -> str:
    """
    Builds a cinematic video from scene images with audio and subtitles.

    Args:
        image_paths:  Absolute paths to generated scene images.
        style:        Style label (for logging only).
        audio_path:   Path to narration.mp3 from voice_generator.
        scene_texts:  Raw scene descriptions for subtitles, one per image.

    Returns:
        Public URL for the final_video.mp4 served by FastAPI StaticFiles.
    """
    if not image_paths:
        raise ValueError("[video_creator] No images provided — cannot create video.")

    print("[video_creator] Creating cinematic clips...")

    # ── Step 1: Calculate per-scene duration from narration ───────────────────
    narration_audio = None
    if audio_path and os.path.exists(audio_path):
        narration_audio = AudioFileClip(audio_path)
        n = len(image_paths)
        # Account for crossfade overlap: each transition removes CROSSFADE_SECS
        # from the total length, so we must add it back into each scene duration.
        # Formula: n * duration - (n-1) * crossfade = narration_duration
        # → duration = (narration_duration + (n-1) * crossfade) / n
        scene_duration  = (narration_audio.duration + (n - 1) * CROSSFADE_SECS) / n
        print(
            f"[video_creator] Narration: {narration_audio.duration:.1f}s  "
            f"| {n} scenes  |  {scene_duration:.2f}s per scene"
        )
    else:
        scene_duration = DEFAULT_DURATION
        print(f"[video_creator] No narration — using {DEFAULT_DURATION}s per scene.")

    # ── Step 2: Build one clip per scene ──────────────────────────────────────
    clips = []
    for i, img_path in enumerate(image_paths):

        # Ken Burns zoom
        scene_clip = _make_zoom_clip(img_path, scene_duration)

        # Subtitle bar pinned to the bottom
        if scene_texts and i < len(scene_texts):
            subtitle_text = _clean_text(scene_texts[i])
            subtitle      = _make_subtitle_clip(subtitle_text, scene_duration)
            scene_clip    = CompositeVideoClip(
                [scene_clip, subtitle],
                size=VIDEO_SIZE,
                use_bgclip=True,
            )

        # CrossFade from scene 2 onward
        if i > 0:
            scene_clip = scene_clip.with_effects([CrossFadeIn(CROSSFADE_SECS)])

        clips.append(scene_clip)

    print("[video_creator] Applying zoom effect and transitions...")

    # ── Step 3: Concatenate with crossfade overlap ────────────────────────────
    final_clip = concatenate_videoclips(
        clips,
        method="compose",
        padding=-CROSSFADE_SECS,
    )

    # ── Step 4: Merge narration audio ──────────────────────────────────────────
    if narration_audio is not None:
        print("[video_creator] Syncing narration audio...")

        # Trim if narration is longer than the assembled clip
        if narration_audio.duration > final_clip.duration:
            narration_audio = narration_audio.subclipped(0, final_clip.duration)

        # Optional background music
        bg_path = get_output_path("background_music.mp3")
        if os.path.exists(bg_path):
            bg = (
                AudioFileClip(bg_path)
                .subclipped(0, final_clip.duration)
                .with_multiply_volume(BG_MUSIC_VOL)
            )
            final_audio = CompositeAudioClip([narration_audio, bg])
        else:
            final_audio = narration_audio

        final_clip = final_clip.with_audio(final_audio)

    # ── Step 5: Export ─────────────────────────────────────────────────────────
    output_path = get_output_path(FINAL_FILENAME)

    final_clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",          # higher bitrate = better quality
        audio_bitrate="192k",
        logger=None,
    )

    final_clip.close()
    print(f"[video_creator] Final video exported → {output_path}")

    return f"http://localhost:8000/outputs/{FINAL_FILENAME}"


# ── Private helpers ──────────────────────────────────────────────────────────

def _make_zoom_clip(img_path: str, duration: float) -> ImageClip:
    """Ken Burns slow zoom: 100% → 105%, keeps frame dimensions constant."""
    # Open with PIL first to resize to our target resolution (avoids dimension mismatches)
    pil_img = Image.open(img_path).convert("RGB").resize(VIDEO_SIZE, Image.LANCZOS)
    arr     = np.array(pil_img)

    clip = ImageClip(arr, duration=duration)
    w, h = clip.size

    # Grow from 100% to 105% over time
    clip = clip.resized(lambda t: 1 + 0.05 * (t / duration))

    # Crop back to original size (centred) so dimensions never change
    clip = clip.cropped(
        x_center=w / 2,
        y_center=h / 2,
        width=w,
        height=h,
    )
    return clip


def _clean_text(text: str) -> str:
    """Remove 'Scene X:' / 'Scene X -' prefixes; trim to max 88 chars."""
    cleaned = re.sub(r"(?i)^scene\s*\d+\s*[:\-]\s*", "", text.strip())
    if len(cleaned) > 88:
        cleaned = cleaned[:85] + "…"
    return cleaned


def _make_subtitle_clip(text: str, duration: float) -> ImageClip:
    """
    Pillow-rendered subtitle bar — no ImageMagick needed.
    Semi-transparent dark bar at the very bottom of the frame, white text.
    """
    bar = Image.new("RGBA", (VIDEO_W, SUBTITLE_H), (0, 0, 0, 170))
    draw = ImageDraw.Draw(bar)

    try:
        font = ImageFont.truetype("arial.ttf", 17)
    except Exception:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 17)
        except Exception:
            font = ImageFont.load_default()

    # Center text vertically inside bar
    draw.text((14, 14), text, fill=(255, 255, 255, 255), font=font)

    rgb = np.array(bar.convert("RGB"))

    y_pos = VIDEO_H - SUBTITLE_H - SUBTITLE_MARGIN   # pinned to bottom

    return (
        ImageClip(rgb, duration=duration)
        .with_position(("center", y_pos))
    )
