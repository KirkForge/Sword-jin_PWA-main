#!/usr/bin/env python3
"""
generate_more_concept4.py
Batch-generate additional story/concept key art for Swordjin (fourth wave).
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/concept/
"""

import base64
import re
import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

API_KEY_PATH = Path("/home/kirk/Madlab/Lockdown/.minimax")
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "concept"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (640, 360)


def load_api_key() -> str:
    if not API_KEY_PATH.exists():
        raise FileNotFoundError(f"API key not found at {API_KEY_PATH}")
    text = API_KEY_PATH.read_text().strip()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            if key.strip().lower() in ("api_key", "key", "minimax_api_key"):
                return value.strip()
        if re.match(r"^sk-[A-Za-z0-9_-]+", line):
            return line
    return text.splitlines()[0].strip()


def generate_image(prompt: str, api_key: str) -> Image.Image:
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "image-01",
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "response_format": "base64",
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    b64_list = data.get("data", {}).get("image_base64", [])
    if not b64_list:
        raise RuntimeError(f"No image returned: {data}")
    raw = base64.b64decode(b64_list[0])
    img = Image.open(BytesIO(raw))
    return img.convert("RGB")


def resize_with_letterbox(img: Image.Image, target: tuple) -> Image.Image:
    target_w, target_h = target
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        new_w = target_w
        new_h = int(target_w / img_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * img_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    bg = Image.new("RGB", (target_w, target_h), (10, 10, 12))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


CONCEPTS = [
    {
        "id": "story_blackwater_departure",
        "name": "Blackwater Departure",
        "prompt": "Cinematic dark fantasy story scene 16:9: a small boat pushing off from a haunted dock into fog with a single lantern, painterly digital art, no text",
    },
    {
        "id": "story_crimson_coronation",
        "name": "Crimson Coronation",
        "prompt": "Cinematic dark fantasy story scene 16:9: a villain placing a crown of thorns and blood upon their own head in a ruined throne room, painterly digital art, no text",
    },
    {
        "id": "story_duel_at_mourning_fields",
        "name": "Duel at Mourning Fields",
        "prompt": "Cinematic dark fantasy story scene 16:9: two warriors facing each other in a field of white memorial stones under a grey sky, painterly digital art, no text",
    },
    {
        "id": "story_legion_last_stand",
        "name": "Legion Last Stand",
        "prompt": "Cinematic dark fantasy story scene 16:9: spectral soldiers forming a shield wall against a tide of shadows, hopelessly outnumbered, painterly digital art, no text",
    },
    {
        "id": "story_mirror_confession",
        "name": "Mirror Confession",
        "prompt": "Cinematic dark fantasy story scene 16:9: a warrior staring into a cracked mirror while their reflection speaks truths they refuse to hear, painterly digital art, no text",
    },
    {
        "id": "story_song_of_surrender",
        "name": "Song of Surrender",
        "prompt": "Cinematic dark fantasy story scene 16:9: an army laying down swords as a siren sings from a cliff above, bittersweet, painterly digital art, no text",
    },
    {
        "id": "story_tear_sealed",
        "name": "Tear Sealed",
        "prompt": "Cinematic dark fantasy story scene 16:9: a crimson rift in the sky slowly closing as light pours through, a figure kneeling below, painterly digital art, no text",
    },
    {
        "id": "story_widows_last_oath",
        "name": "Widow's Last Oath",
        "prompt": "Cinematic dark fantasy story scene 16:9: a black-veiled widow kneeling before a fallen soldier's sword and swearing vengeance, painterly digital art, no text",
    },
    {
        "id": "title_crimson_throne",
        "name": "Crimson Throne",
        "prompt": "Cinematic dark fantasy title/key art 16:9: a throne room soaked in red light with a shadowed figure ascending blood-stained steps, painterly digital art, no text",
    },
    {
        "id": "title_hollow_hero",
        "name": "Hollow Hero",
        "prompt": "Cinematic dark fantasy title/key art 16:9: a once-heroic warrior hollowed by sacrifice walking away into mist, painterly digital art, no text",
    },
    {
        "id": "title_legion_requiem",
        "name": "Legion Requiem",
        "prompt": "Cinematic dark fantasy title/key art 16:9: spectral soldiers bowing their heads as their banners dissolve into stardust, painterly digital art, no text",
    },
    {
        "id": "title_memory_and_tear",
        "name": "Memory and Tear",
        "prompt": "Cinematic dark fantasy title/key art 16:9: a warrior holding a glowing memory shard beneath a weeping crimson sky, painterly digital art, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for concept in CONCEPTS:
        path = OUT_DIR / f"{concept['id']}.webp"
        if path.exists():
            print(f"Skipping {concept['id']} (exists)")
            continue

        print(f"\nGenerating concept: {concept['name']}")
        try:
            img = generate_image(concept["prompt"], api_key)
            fitted = resize_with_letterbox(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {concept['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
