#!/usr/bin/env python3
"""
generate_more_locations4.py
Batch-generate additional location/zone marker icons for Swordjin (fourth wave).
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
        "id": "loc_ashen_crematory",
        "name": "Ashen Crematory",
        "prompt": "Pixel-art style RPG location icon on dark background: a kiln of black stone with smoke rising and bones piled at the base, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_blood_tide_reach",
        "name": "Blood-Tide Reach",
        "prompt": "Pixel-art style RPG location icon on dark background: a coastline where red waves crash against jagged black rocks, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_carrion_fields",
        "name": "Carrion Fields",
        "prompt": "Pixel-art style RPG location icon on dark background: a battlefield of picked-clean bones and circling carrion birds, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_crypt_of_echoes",
        "name": "Crypt of Echoes",
        "prompt": "Pixel-art style RPG location icon on dark background: a mausoleum entrance with whispering blue spirits drifting from it, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_fang_throne",
        "name": "Fang Throne",
        "prompt": "Pixel-art style RPG location icon on dark background: a throne carved from a single massive fang, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_hollow_ford",
        "name": "Hollow Ford",
        "prompt": "Pixel-art style RPG location icon on dark background: a shallow river crossing with submerged helmets and ghostly hands reaching up, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_iron_watchtower",
        "name": "Iron Watchtower",
        "prompt": "Pixel-art style RPG location icon on dark background: a rusted metal tower with a single beacon flame at the top, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_moonlit_market",
        "name": "Moonlit Market",
        "prompt": "Pixel-art style RPG location icon on dark background: a night market of tents and glowing lanterns under a full moon, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_pit_of_chains",
        "name": "Pit of Chains",
        "prompt": "Pixel-art style RPG location icon on dark background: a deep pit lined with hanging iron chains and red glow from below, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_silent_mill",
        "name": "Silent Mill",
        "prompt": "Pixel-art style RPG location icon on dark background: a ruined windmill with torn sails and crows on the roof, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_throne_of_memory",
        "name": "Throne of Memory",
        "prompt": "Pixel-art style RPG location icon on dark background: a crystalline throne floating in a void surrounded by memory shards, centered, game map location icon, 1:1, no text",
    },
    {
        "id": "loc_veilgate",
        "name": "Veilgate",
        "prompt": "Pixel-art style RPG location icon on dark background: a stone archway draped in tattered white cloth leading into fog, centered, game map location icon, 1:1, no text",
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
