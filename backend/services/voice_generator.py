"""
services/voice_generator.py
----------------------------
Responsibility:
  Takes the user's script and converts it to speech using Google Text-to-Speech (gTTS).
"""

import os
from gtts import gTTS
from utils.file_manager import get_output_path

def generate_voice(script: str) -> str:
    """
    Converts the script text into speech and saves it as an MP3.

    Args:
        script: The user's input script.

    Returns:
        The full absolute path to the generated narration.mp3 file.
    """
    print("[voice_generator] Generating narration...")

    # We use a static filename for now, but in a real app this should be unique per request.
    output_filename = "narration.mp3"
    output_path = get_output_path(output_filename)

    # Convert text to speech
    tts = gTTS(text=script, lang='en')
    tts.save(output_path)

    print(f"[voice_generator] Audio saved to {output_path}")

    return output_path
