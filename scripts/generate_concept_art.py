#!/usr/bin/env python3
"""
generate_concept_art.py
Batch-generate high-impact concept / key art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/concept/
"""

import base64
import json
import os
import re
import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

API_KEY_PATH = Path("/home/kirk/Madlab/Lockdown/.minimax")
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "concept"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (640, 360)


def safe_filename(title: str) -> str:
    base = title.lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_\.]", "", base)


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


def fit_to_resolution(img: Image.Image) -> Image.Image:
    img.thumbnail(RESOLUTION, Image.LANCZOS)
    bg = Image.new("RGB", RESOLUTION, (10, 10, 15))
    x = (RESOLUTION[0] - img.width) // 2
    y = (RESOLUTION[1] - img.height) // 2
    bg.paste(img, (x, y))
    return bg


CONCEPTS = [
    {
        "name": "title_hero_sword",
        "prompt": "Dark fantasy title key art: lone warrior Jin holding the cursed Sword of Ruin aloft, blade glowing with inner red light, wind sweeping a ruined battlefield at sunset, raven flying overhead, cinematic 16:9, painterly digital art, no text",
    },
    {
        "name": "title_ruined_throne",
        "prompt": "Dark fantasy title key art: an empty imperial throne room in ruins, the Sword of Ruin resting on the throne steps, shafts of dawn light through broken windows, dust motes, melancholy atmosphere, painterly digital art, 16:9, no text",
    },
    {
        "name": "title_dark_tower",
        "prompt": "Dark fantasy title key art: a colossal obsidian tower piercing storm clouds, lightning at the summit, tiny silhouetted warrior at the base, apocalyptic scale, painterly digital art, 16:9, no text",
    },
    {
        "name": "title_alliance_banners",
        "prompt": "Dark fantasy title key art: three armies united under imperial, merchant, and bandit banners marching across a sunlit ridge, epic scope, painterly digital art, 16:9, no text",
    },
    {
        "name": "story_merchant_plea",
        "prompt": "Dark fantasy story moment: Jin kneeling beside an injured merchant on a muddy forest road, bandits approaching through mist, lantern light warm against cold blue shadows, emotional painterly digital art, 16:9, no text",
    },
    {
        "name": "story_first_draw",
        "prompt": "Dark fantasy story moment: Jin drawing the cursed Sword of Ruin for the first time, black energy spiraling around the blade, onlookers recoiling in terror, dramatic painterly digital art, 16:9, no text",
    },
    {
        "name": "story_wraith_binding",
        "prompt": "Dark fantasy story moment: a Crimson Fang priest binding a spectral wraith inside an iron cage of runes, ghostly light illuminating a stone shrine, painterly digital art, 16:9, no text",
    },
    {
        "name": "story_siege_breach",
        "prompt": "Dark fantasy story moment: imperial legions charging through a shattered city gate, siege towers burning, defenders falling back, epic battle chaos, painterly digital art, 16:9, no text",
    },
    {
        "name": "story_void_memory",
        "prompt": "Dark fantasy story moment: Jin floating in a void realm of fractured memories, golden and purple shards showing ancient forges and betrayals, ethereal painterly digital art, 16:9, no text",
    },
    {
        "name": "character_jin_portrait",
        "prompt": "Dark fantasy character portrait: Jin, a weathered mercenary with sharp eyes and a scar across his cheek, leather armor, holding a plain sword, neutral determined expression, painterly digital art, centered bust, simple dark background, 16:9, no text",
    },
    {
        "name": "character_merchant_ally",
        "prompt": "Dark fantasy character portrait: an older merchant ally with kind weary eyes, travel cloak, ledger and coin purse, friendly half-smile, painterly digital art, centered bust, simple dark background, 16:9, no text",
    },
    {
        "name": "character_fang_priest",
        "prompt": "Dark fantasy character portrait: a Crimson Fang priest wearing a carved bone fang mask, hooded crimson robes, holding a gnarled staff, menacing stillness, painterly digital art, centered bust, simple dark background, 16:9, no text",
    },
    {
        "name": "character_master_of_fang",
        "prompt": "Dark fantasy character portrait: the Master of the Crimson Fang, a gaunt noble in black armor lined with red silk, pale hands clasped, cruel intelligence in the eyes, painterly digital art, centered bust, simple dark background, 16:9, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for concept in CONCEPTS:
        path = OUT_DIR / f"{concept['name']}.webp"
        if path.exists():
            print(f"Skipping {concept['name']} (exists)")
            continue

        print(f"\nGenerating concept: {concept['name']}")
        try:
            img = generate_image(concept["prompt"], api_key)
            bg = fit_to_resolution(img)
            bg.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {concept['name']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
