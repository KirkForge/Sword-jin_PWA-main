#!/usr/bin/env python3
"""
generate_more_locations.py
Batch-generate additional location/zone icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/locations/
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
    bg = Image.new("RGB", (size, size), (22, 22, 26))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


LOCATIONS = [
    {
        "id": "loc_crypt_of_kings",
        "name": "Crypt of Kings",
        "prompt": "Pixel-art style RPG location icon on dark background: an ancient stone mausoleum with cracked pillars and ghostly blue lanterns, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_forest_wardens",
        "name": "Wardens' Grove",
        "prompt": "Pixel-art style RPG location icon on dark background: a dense twisted forest with glowing eyes between trees and mist, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_iron_mines",
        "name": "Iron Mines",
        "prompt": "Pixel-art style RPG location icon on dark background: a dark mine entrance with cart tracks and orange torchlight, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_sunken_cathedral",
        "name": "Sunken Cathedral",
        "prompt": "Pixel-art style RPG location icon on dark background: half-submerged gothic cathedral with a broken spire and green water, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_obsidian_forge",
        "name": "Obsidian Forge",
        "prompt": "Pixel-art style RPG location icon on dark background: a blacksmith forge built from volcanic rock with rivers of lava, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_moonlit_market",
        "name": "Moonlit Market",
        "prompt": "Pixel-art style RPG location icon on dark background: a nighttime bazaar with colorful tents and hanging lanterns, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_hollow_peak",
        "name": "Hollow Peak",
        "prompt": "Pixel-art style RPG location icon on dark background: a jagged mountain peak with a hollow eye-shaped cave and snow, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_ashmont_keep",
        "name": "Ashmont Keep",
        "prompt": "Pixel-art style RPG location icon on dark background: a dark fortress keep with ash falling from a crimson sky, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_fallow_fields",
        "name": "Fallow Fields",
        "prompt": "Pixel-art style RPG location icon on dark background: a dead battlefield with scattered weapons and crows under grey clouds, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_whispering_docks",
        "name": "Whispering Docks",
        "prompt": "Pixel-art style RPG location icon on dark background: a foggy harbor pier with creaking ships and green witch-lights, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_throne_of_echoes",
        "name": "Throne of Echoes",
        "prompt": "Pixel-art style RPG location icon on dark background: an empty stone throne in a vast hall with spectral whispers and blue mist, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_crimson_tear",
        "name": "Crimson Tear",
        "prompt": "Pixel-art style RPG location icon on dark background: a dimensional wound in the sky bleeding red light onto ruined ground, centered, game map location icon, 1:1, no text",
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
