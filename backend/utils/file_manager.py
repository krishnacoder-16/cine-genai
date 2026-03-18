"""
utils/file_manager.py
----------------------
Responsibility:
  Centralises all file path construction and folder creation.

  Every service that writes a file uses this utility instead of
  hardcoding paths — this keeps file management in one place.

Functions:
  • get_output_path(filename) → ensures outputs/ folder exists,
                                returns the full path for a file inside it.

The outputs/ folder is where all generated images and videos are saved.
It is created automatically on first use.
"""

import os

# ── Base directory: the backend/ folder itself ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Where all generated files land ─────────────────────────────────────────
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def get_output_path(filename: str) -> str:
    """
    Returns the full absolute path for a file inside the outputs/ directory.
    Creates the outputs/ folder automatically if it doesn't exist yet.

    Args:
        filename: Just the filename, e.g. "scene_1_cinematic.png"

    Returns:
        Full path, e.g. "C:/cinegen-ai/backend/outputs/scene_1_cinematic.png"

    Example:
        path = get_output_path("video_cinematic_output.mp4")
        # Returns: C:/cinegen-ai/backend/outputs/video_cinematic_output.mp4
    """
    # Create the folder if it doesn't already exist
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    return os.path.join(OUTPUTS_DIR, filename)


def clean_outputs() -> int:
    """
    Deletes all files inside the outputs/ directory.
    Useful for clearing temp files between runs.

    Returns:
        Number of files deleted.
    """
    if not os.path.exists(OUTPUTS_DIR):
        return 0

    count = 0
    for filename in os.listdir(OUTPUTS_DIR):
        file_path = os.path.join(OUTPUTS_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            count += 1

    return count
