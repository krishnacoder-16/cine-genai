import re
from services.consistency_engine import register_character

def extract_character(scene_text):
    """
    naive character extractor
    (can upgrade later with LLM)
    """

    match = re.search(r"(detective|hero|girl|boy|scientist)", scene_text.lower())

    if match:
        character = match.group(1)

        description = f"{character}, cinematic lighting, highly detailed face"

        register_character(character, description)

        return character

    return None