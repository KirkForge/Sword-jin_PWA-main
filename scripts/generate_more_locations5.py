#!/usr/bin/env python3
"""
generate_more_locations5.py
Batch-generate additional location/zone marker icons for Swordjin (fifth wave).
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
    {"id": "loc_abandoned_lighthouse", "name": "Abandoned Lighthouse", "prompt": "Pixel-art style RPG location icon on dark background: a leaning lighthouse with a cracked lens casting a pale beam over churning waves, centered, game map location icon, 1:1, no text"},
    {"id": "loc_beggars_rest", "name": "Beggar's Rest", "prompt": "Pixel-art style RPG location icon on dark background: a huddle of tents around a shared fire in a muddy hollow, centered, game map location icon, 1:1, no text"},
    {"id": "loc_crimson_foundry", "name": "Crimson Foundry", "prompt": "Pixel-art style RPG location icon on dark background: a foundry with rivers of glowing red metal and soot-blackened chimneys, centered, game map location icon, 1:1, no text"},
    {"id": "loc_desecrated_shrine", "name": "Desecrated Shrine", "prompt": "Pixel-art style RPG location icon on dark background: a once-holy shrine defaced with black ichor and broken offerings, centered, game map location icon, 1:1, no text"},
    {"id": "loc_forsaken_manor", "name": "Forsaken Manor", "prompt": "Pixel-art style RPG location icon on dark background: a dilapidated mansion with boarded windows and a crooked weathervane, centered, game map location icon, 1:1, no text"},
    {"id": "loc_glass_citadel", "name": "Glass Citadel", "prompt": "Pixel-art style RPG location icon on dark background: a citadel of translucent crystal spires reflecting a fractured sky, centered, game map location icon, 1:1, no text"},
    {"id": "loc_hangmans_yard", "name": "Hangman's Yard", "prompt": "Pixel-art style RPG location icon on dark background: a yard of gallows with empty nooses swaying in fog, centered, game map location icon, 1:1, no text"},
    {"id": "loc_inferno_caldera", "name": "Inferno Caldera", "prompt": "Pixel-art style RPG location icon on dark background: a volcanic crater with a lake of fire and floating cinders, centered, game map location icon, 1:1, no text"},
    {"id": "loc_obsidian_terrace", "name": "Obsidian Terrace", "prompt": "Pixel-art style RPG location icon on dark background: a black glass terrace overlooking a stormy abyss, centered, game map location icon, 1:1, no text"},
    {"id": "loc_siren_reef", "name": "Siren Reef", "prompt": "Pixel-art style RPG location icon on dark background: jagged rocks jutting from churning seas with ghostly figures singing, centered, game map location icon, 1:1, no text"},
    {"id": "loc_tower_of_mourning", "name": "Tower of Mourning", "prompt": "Pixel-art style RPG location icon on dark background: a tall black tower wrapped in funeral shrouds and black flags, centered, game map location icon, 1:1, no text"},
    {"id": "loc_vault_of_souls", "name": "Vault of Souls", "prompt": "Pixel-art style RPG location icon on dark background: a bank vault door with glowing souls visible through the bars, centered, game map location icon, 1:1, no text"},
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
