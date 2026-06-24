#!/usr/bin/env python3
"""
generate_more_locations2.py
Batch-generate additional location/zone marker icons for Swordjin.
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
        "id": "loc_crimson_marshes",
        "name": "Crimson Marshes",
        "prompt": "Pixel-art style RPG location icon on dark background: a swamp with red water, twisted trees and will-o-wisps, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_frostpeak_pass",
        "name": "Frostpeak Pass",
        "prompt": "Pixel-art style RPG location icon on dark background: a snowy mountain pass with a narrow trail and ice formations, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_ember_quarry",
        "name": "Ember Quarry",
        "prompt": "Pixel-art style RPG location icon on dark background: an open quarry with glowing embers and broken stone columns, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_mourning_fields",
        "name": "Mourning Fields",
        "prompt": "Pixel-art style RPG location icon on dark background: a grey field of grave markers under a weeping sky, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_thornwall",
        "name": "Thornwall",
        "prompt": "Pixel-art style RPG location icon on dark background: a fortress wall overgrown with massive black thorns, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_shattered_spire",
        "name": "Shattered Spire",
        "prompt": "Pixel-art style RPG location icon on dark background: a broken wizard tower with lightning at its peak, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_pilgrims_rest",
        "name": "Pilgrim's Rest",
        "prompt": "Pixel-art style RPG location icon on dark background: a small shrine by a road with a lit lantern and well, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_mire_of_echoes",
        "name": "Mire of Echoes",
        "prompt": "Pixel-art style RPG location icon on dark background: a foggy swamp with ghostly reflections and sunken statues, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_sunfall_bastion",
        "name": "Sunfall Bastion",
        "prompt": "Pixel-art style RPG location icon on dark background: a half-ruined bastion bathed in red sunset light, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_widows_wood",
        "name": "Widow's Wood",
        "prompt": "Pixel-art style RPG location icon on dark background: a dark forest with hanging moss and pale mourning figures, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_the_scar",
        "name": "The Scar",
        "prompt": "Pixel-art style RPG location icon on dark background: a jagged canyon of red rock with a river of black glass at bottom, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_hopeful_dawn",
        "name": "Hopeful Dawn",
        "prompt": "Pixel-art style RPG location icon on dark background: a hilltop camp with a single ray of golden sunrise breaking clouds, centered, game map location icon, 1:1, no text",
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
