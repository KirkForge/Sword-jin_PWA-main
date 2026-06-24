#!/usr/bin/env python3
"""
generate_modifier_icons.py
Batch-generate daily challenge modifier icons for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/ui/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "ui"
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
    bg = Image.new("RGB", (size, size), (20, 20, 25))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


MODIFIERS = [
    {
        "id": "mod_double_damage",
        "name": "Double Damage",
        "prompt": "Pixel-art style RPG modifier icon on dark background: two crossed swords glowing red with a damage burst aura, centered, game UI icon, 1:1, no text",
    },
    {
        "id": "mod_half_health",
        "name": "Half Health",
        "prompt": "Pixel-art style RPG modifier icon on dark background: a cracked red heart with a slash through it, centered, game UI icon, 1:1, no text",
    },
    {
        "id": "mod_speed_run",
        "name": "Speed Run",
        "prompt": "Pixel-art style RPG modifier icon on dark background: a winged hourglass with motion lines, centered, game UI icon, 1:1, no text",
    },
    {
        "id": "mod_no_potions",
        "name": "No Potions",
        "prompt": "Pixel-art style RPG modifier icon on dark background: a potion bottle with a red prohibition sign over it, centered, game UI icon, 1:1, no text",
    },
    {
        "id": "mod_enemy_swarm",
        "name": "Enemy Swarm",
        "prompt": "Pixel-art style RPG modifier icon on dark background: three aggressive skull silhouettes with a plus sign, centered, game UI icon, 1:1, no text",
    },
    {
        "id": "mod_glass_cannon",
        "name": "Glass Cannon",
        "prompt": "Pixel-art style RPG modifier icon on dark background: a shattered glass cannon barrel glowing with unstable energy, centered, game UI icon, 1:1, no text",
    },
    {
        "id": "mod_gold_rush",
        "name": "Gold Rush",
        "prompt": "Pixel-art style RPG modifier icon on dark background: a golden coin shower with sparkles and a treasure bag, centered, game UI icon, 1:1, no text",
    },
    {
        "id": "mod_iron_man",
        "name": "Iron Man",
        "prompt": "Pixel-art style RPG modifier icon on dark background: a steel helmet with a single life counter of 1, centered, game UI icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for item in MODIFIERS:
        path = OUT_DIR / f"{item['id']}.webp"
        if path.exists():
            print(f"Skipping {item['id']} (exists)")
            continue

        print(f"\nGenerating modifier: {item['name']}")
        try:
            img = generate_image(item["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {item['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
