#!/usr/bin/env python3
"""
generate_skill_icons.py
Batch-generate combat skill/ability icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/skills/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "skills"
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
    bg = Image.new("RGB", (size, size), (20, 20, 25))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


SKILLS = [
    {
        "id": "skill_slash",
        "name": "Slash",
        "prompt": "Pixel-art style RPG ability icon on dark background: a swift sword slash, silver blade trail with motion lines, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_whirlwind",
        "name": "Whirlwind",
        "prompt": "Pixel-art style RPG ability icon on dark background: a spinning steel whirlwind, circular blade storm, grey and silver, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_shield_bash",
        "name": "Shield Bash",
        "prompt": "Pixel-art style RPG ability icon on dark background: a steel kite shield slamming forward with a blue impact burst, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_parry",
        "name": "Parry",
        "prompt": "Pixel-art style RPG ability icon on dark background: crossed swords blocking an incoming strike, orange spark, defensive stance, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_fire_strike",
        "name": "Fire Strike",
        "prompt": "Pixel-art style RPG ability icon on dark background: a blazing sword wreathed in orange flame, ember particles, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_ice_shard",
        "name": "Ice Shard",
        "prompt": "Pixel-art style RPG ability icon on dark background: a jagged cyan ice crystal shard flying forward, frost mist, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_lightning_strike",
        "name": "Lightning Strike",
        "prompt": "Pixel-art style RPG ability icon on dark background: a jagged violet lightning bolt striking down, electric glow, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_healing_light",
        "name": "Healing Light",
        "prompt": "Pixel-art style RPG ability icon on dark background: a golden glowing hand radiating warm light and healing sparks, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_taunt",
        "name": "Taunt",
        "prompt": "Pixel-art style RPG ability icon on dark background: a roaring armored helmet with red aggression waves, battle cry, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_execute",
        "name": "Execute",
        "prompt": "Pixel-art style RPG ability icon on dark background: a greatsword raised for a lethal finishing blow, dripping red edge, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_smoke_bomb",
        "name": "Smoke Bomb",
        "prompt": "Pixel-art style RPG ability icon on dark background: a thrown glass bomb shattering into grey smoke clouds, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_rally",
        "name": "Rally",
        "prompt": "Pixel-art style RPG ability icon on dark background: raised sword with golden banner and inspiring light, leadership aura, centered, game skill icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for skill in SKILLS:
        path = OUT_DIR / f"{skill['id']}.webp"
        if path.exists():
            print(f"Skipping {skill['id']} (exists)")
            continue

        print(f"\nGenerating skill: {skill['name']}")
        try:
            img = generate_image(skill["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {skill['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
