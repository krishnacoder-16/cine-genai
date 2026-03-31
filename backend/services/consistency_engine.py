import hashlib
import random

# stores character profiles during session
CHARACTER_MEMORY = {}

def generate_seed(character_name: str):
    """
    Generates deterministic seed from character name
    """
    hash_object = hashlib.md5(character_name.encode())
    seed = int(hash_object.hexdigest(), 16) % (10**8)
    return seed


def register_character(name, description):
    """
    Save character appearance permanently
    """
    if name not in CHARACTER_MEMORY:
        CHARACTER_MEMORY[name] = {
            "description": description,
            "seed": generate_seed(name)
        }

    return CHARACTER_MEMORY[name]


def enhance_prompt(prompt: str):
    """
    Injects consistency info into prompt
    """

    for character in CHARACTER_MEMORY:
        if character.lower() in prompt.lower():

            profile = CHARACTER_MEMORY[character]

            prompt += f"""
 cinematic character consistency,
 same face,
 same costume,
 {profile['description']}
 """

            return prompt, profile["seed"]

    # no character found
    return prompt, random.randint(1, 9999999)