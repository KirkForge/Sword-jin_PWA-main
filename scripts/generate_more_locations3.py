#!/usr/bin/env python3
"""
generate_more_locations3.py
Batch-generate additional location/zone marker icons for Swordjin (third wave).
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
        "id": "loc_bloodroot_grove",
        "name": "Bloodroot Grove",
        "prompt": "Pixel-art style RPG location icon on dark background: a forest of trees with crimson leaves and thorny roots, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_grave_of_storms",
        "name": "Grave of Storms",
        "prompt": "Pixel-art style RPG location icon on dark background: a desolate plain with lightning striking ancient monoliths, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_sunken_archive",
        "name": "Sunken Archive",
        "prompt": "Pixel-art style RPG location icon on dark background: a flooded library with floating books and blue ghost-lights, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_bramble_citadel",
        "name": "Bramble Citadel",
        "prompt": "Pixel-art style RPG location icon on dark background: a fortress consumed by thick vines and blooming poisonous flowers, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_hollow_march",
        "name": "Hollow March",
        "prompt": "Pixel-art style RPG location icon on dark background: a road lined with empty suits of armor standing in salute, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_weeping_sanctum",
        "name": "Weeping Sanctum",
        "prompt": "Pixel-art style RPG location icon on dark background: a ruined chapel with water pouring from angel statues' eyes, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_forgotten_dockyard",
        "name": "Forgotten Dockyard",
        "prompt": "Pixel-art style RPG location icon on dark background: a rotting pier with beached ships and hanging nets, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_cinder_expanse",
        "name": "Cinder Expanse",
        "prompt": "Pixel-art style RPG location icon on dark background: a field of black ash with drifting embers and cracked ground, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_gallows_crossing",
        "name": "Gallows Crossing",
        "prompt": "Pixel-art style RPG location icon on dark background: a rope bridge over a chasm with gallows posts and crows, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_orchard_of_lies",
        "name": "Orchard of Lies",
        "prompt": "Pixel-art style RPG location icon on dark background: an orchard of trees with faces in the bark and silver apples, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_marrow_pits",
        "name": "Marrow Pits",
        "prompt": "Pixel-art style RPG location icon on dark background: a cavern floor dotted with holes and pale bone spires, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_dawnward_gate",
        "name": "Dawnward Gate",
        "prompt": "Pixel-art style RPG location icon on dark background: a massive gate opening onto a golden sunrise, centered, game map location icon, 1:1, no text",
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
