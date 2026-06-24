#!/usr/bin/env python3
"""
generate_achievement_icons.py
Batch-generate achievement/badge icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/achievements/
"""

import base64
import os
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


def safe_filename(name: str) -> str:
    base = name.lower().replace(" ", "_")
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
    bg = Image.new("RGB", (size, size), (25, 22, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


ACHIEVEMENTS = [
    {
        "id": "ach_first_blood",
        "name": "First Blood",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a bronze medallion with a single drop of blood and a crossed sword, centered, no text",
    },
    {
        "id": "ach_champion",
        "name": "Champion",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a golden laurel wreath around a gleaming crown, centered, no text",
    },
    {
        "id": "ach_completionist",
        "name": "Completionist",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a platinum shield covered in completion checkmarks and stars, centered, no text",
    },
    {
        "id": "ach_boss_slayer",
        "name": "Boss Slayer",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a monstrous horned skull impaled by a greatsword, centered, no text",
    },
    {
        "id": "ach_daily_warrior",
        "name": "Daily Warrior",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a silver sun rising behind a crossed sword and shield, centered, no text",
    },
    {
        "id": "ach_treasure_hunter",
        "name": "Treasure Hunter",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: an overflowing chest of gold coins, rubies, and a glowing key, centered, no text",
    },
    {
        "id": "ach_iron_will",
        "name": "Iron Will",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a steel anvil with a hammer strike and sparks, centered, no text",
    },
    {
        "id": "ach_shadow_walker",
        "name": "Shadow Walker",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a hooded silhouette fading into black smoke and violet eyes, centered, no text",
    },
    {
        "id": "ach_ruins_conqueror",
        "name": "Ruins Conqueror",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a crumbling stone tower with a victory banner on top, centered, no text",
    },
    {
        "id": "ach_true_ending",
        "name": "True Ending",
        "prompt": "Pixel-art style RPG achievement badge icon on dark background: a radiant sunrise breaking over a dark horizon, golden and hopeful, centered, no text",
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
