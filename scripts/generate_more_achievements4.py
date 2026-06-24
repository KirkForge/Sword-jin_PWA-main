#!/usr/bin/env python3
"""
generate_more_achievements4.py
Batch-generate additional achievement badge icons for Swordjin (fourth wave).
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/achievements/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "achievements"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (128, 128)


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
        "aspect_ratio": "1:1",
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


def fit_square(img: Image.Image, size: int = 128) -> Image.Image:
    img.thumbnail((size, size), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (25, 20, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


ACHIEVEMENTS = [
    {
        "id": "ach_blood_donor",
        "name": "Blood Donor",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a bleeding heart offering a single red drop to a clay cup, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_ghost_talker",
        "name": "Ghost Talker",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a skull with a speech bubble containing a glowing rune, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_mercy_strike",
        "name": "Mercy Strike",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a sword held downward in salute over a fallen foe, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_pactbreaker",
        "name": "Pactbreaker",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a snapped contract scroll with black flames, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_siege_engineer",
        "name": "Siege Engineer",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a small catapult firing a flaming boulder, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_witness",
        "name": "Witness",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a single wide eye reflecting a distant battlefield, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_unchained",
        "name": "Unchained",
        "prompt": "Pixel-art style RPG achievement badge on dark background: broken iron shackles with sparks flying, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_blightwalker",
        "name": "Blightwalker",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a boot stepping through blackened corrupted grass, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_honor_bound",
        "name": "Honor Bound",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a golden ribbon tied around a bloodied sword hilt, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_tide_turner",
        "name": "Tide Turner",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a warrior standing atop a wave of defeated enemies, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_lone_survivor",
        "name": "Lone Survivor",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a single lit candle in a circle of snuffed flames, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_world_remembered",
        "name": "World Remembered",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a glowing globe formed of intertwined roots and memory shards, centered, badge icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for ach in ACHIEVEMENTS:
        path = OUT_DIR / f"{ach['id']}.webp"
        if path.exists():
            print(f"Skipping {ach['id']} (exists)")
            continue

        print(f"\nGenerating achievement: {ach['name']}")
        try:
            img = generate_image(ach["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {ach['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
