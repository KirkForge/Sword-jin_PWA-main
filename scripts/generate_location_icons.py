#!/usr/bin/env python3
"""
generate_location_icons.py
Batch-generate map/location marker art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/locations/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "locations"
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


LOCATIONS = [
    {
        "id": "loc_ruins",
        "name": "Ruins",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: crumbling stone ruins with a broken archway and moss, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_forest",
        "name": "Forest",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a cluster of pine trees with a path leading in, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_city",
        "name": "City",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a walled city with towers and gates under a dusk sky, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_tower",
        "name": "Dark Tower",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a tall sinister black tower with a red glowing peak, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_camp",
        "name": "Camp",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a small adventurer camp with tents and a campfire, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_gate",
        "name": "Great Gate",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a massive iron fortress gate with banners and torches, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_battlefield",
        "name": "Battlefield",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a smoky battlefield with broken weapons and banners, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_void",
        "name": "Void Rift",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a swirling purple void rift with lightning cracks, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_merchant",
        "name": "Merchant Stop",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a merchant cart with goods and a hanging lantern, centered, game map icon, 1:1, no text",
    },
    {
        "id": "loc_shrine",
        "name": "Shrine",
        "prompt": "Pixel-art style RPG map location icon on dark parchment background: a small stone shrine with a glowing blue crystal and offerings, centered, game map icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for loc in LOCATIONS:
        path = OUT_DIR / f"{loc['id']}.webp"
        if path.exists():
            print(f"Skipping {loc['id']} (exists)")
            continue

        print(f"\nGenerating location: {loc['name']}")
        try:
            img = generate_image(loc["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {loc['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
