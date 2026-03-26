"""
services/voice_generator.py
----------------------------
Converts script text to speech using ElevenLabs (high-quality AI voices).
Falls back to gTTS automatically if the API key is missing or the call fails.

Setup:
  1. Get a free API key at https://elevenlabs.io
  2. Add to your .env:  ELEVENLABS_API_KEY=your_key_here
  3. pip install elevenlabs

Voice IDs (free tier — no changes needed):
  Rachel  : 21m00Tcm4TlvDq8ikWAM  — warm, clear, great for narration (default)
  Adam    : pNInz6obpgDQGcFmaJgB  — deep, authoritative
  Bella   : EXAVITQu4vr4xnSDxMaL  — soft, cinematic
  Antoni  : ErXwobaYiN019PkySvjV  — smooth, storytelling
"""

import os
from utils.file_manager import get_output_path

# ── Voice presets — swap VOICE_ID to change the narrator ───────────────────
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"   # Sarah — soft, cinematic
MODEL_ID = "eleven_turbo_v2_5"
OUTPUT_FMT = "mp3_44100_128"


def generate_voice(script: str) -> str:
    """
    Converts the script text into speech and saves it as narration.mp3.

    Args:
        script: Full narration text (all scene subtitles joined).

    Returns:
        Absolute path to the saved narration.mp3.
    """
    print("[voice_generator] Generating narration...")

    output_path = get_output_path("narration.mp3")

    api_key = os.getenv("ELEVENLABS_API_KEY")

    if api_key:
        success = _generate_elevenlabs(script, output_path, api_key)
        if success:
            return output_path
        print("[voice_generator] ⚠️  ElevenLabs failed — falling back to gTTS.")

    # Fallback: gTTS
    _generate_gtts(script, output_path)
    return output_path


# ── ElevenLabs ───────────────────────────────────────────────────────────────

def _generate_elevenlabs(script: str, output_path: str, api_key: str) -> bool:
    """
    Calls ElevenLabs TTS API and writes the audio to output_path.
    Returns True on success, False on any error.
    """
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings

        client = ElevenLabs(api_key=api_key)

        audio_stream = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            text=script,
            voice_settings=VoiceSettings(
                stability=0.5,          # 0–1: higher = more consistent tone
                similarity_boost=0.8,   # 0–1: higher = closer to original voice
                style=0.3,              # 0–1: expressiveness
                use_speaker_boost=True,
            ),
            output_format=OUTPUT_FMT,
        )

        # audio_stream is a generator of bytes chunks — write them all
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        print(f"[voice_generator] ✅ ElevenLabs audio saved to {output_path}")
        return True

    except ImportError:
        print(
            "[voice_generator] ❌ elevenlabs package not installed. Run: pip install elevenlabs")
        return False
    except Exception as e:
        print(f"[voice_generator] ❌ ElevenLabs error: {e}")
        return False


# ── gTTS fallback ─────────────────────────────────────────────────────────────

def _generate_gtts(script: str, output_path: str):
    """Fallback TTS using gTTS (Google). Always works, sounds robotic."""
    from gtts import gTTS
    tts = gTTS(text=script, lang="en")
    tts.save(output_path)
    print(f"[voice_generator] Audio saved to {output_path} (gTTS fallback)")
