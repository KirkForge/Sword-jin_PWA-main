#!/usr/bin/env python3
"""
generate_more_enemies.py
Batch-generate additional enemy creature portraits for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/enemy_portraits/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "enemy_portraits"
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
    bg = Image.new("RGB", (size, size), (18, 18, 22))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


ENEMIES = [
    {
        "id": "enemy_crimson_marauder",
        "name": "Crimson Marauder",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a savage raider with a crimson-painted face and mismatched armor, intense stare, 1:1, no text",
    },
    {
        "id": "enemy_bog_wraith",
        "name": "Bog Wraith",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a dripping spectral figure rising from swamp water, glowing green eyes, tattered cloak, 1:1, no text",
    },
    {
        "id": "enemy_iron_sentinel",
        "name": "Iron Sentinel",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: an ancient rusted knight automaton with a single glowing eye, imposing helmet, 1:1, no text",
    },
    {
        "id": "enemy_gnarlroot_thrall",
        "name": "Gnarlroot Thrall",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a humanoid twisted from wood and roots with red fungal growths, feral expression, 1:1, no text",
    },
    {
        "id": "enemy_siren_harpy",
        "name": "Siren Harpy",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a pale winged woman with sharp teeth and dead eyes, ocean mist in hair, 1:1, no text",
    },
    {
        "id": "enemy_mourning_ash",
        "name": "Mourning Ash",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a humanoid made of ash and cinders with a silently screaming face, ember cracks, 1:1, no text",
    },
    {
        "id": "enemy_plague_hound",
        "name": "Plague Hound",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a gaunt undead hound with exposed ribs and milky eyes, black saliva dripping, 1:1, no text",
    },
    {
        "id": "enemy_void_touched_mage",
        "name": "Void-Touched Mage",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a robed spellcaster with a star-filled void where their face should be, arcane sigils, 1:1, no text",
    },
    {
        "id": "enemy_bramble_titan",
        "name": "Bramble Titan",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a massive hulking creature made of thorns and bark, tiny glowing red eyes, 1:1, no text",
    },
    {
        "id": "enemy_lost_legionnaire",
        "name": "Lost Legionnaire",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a ghostly Roman-style soldier with a translucent spear and hollow eye sockets, 1:1, no text",
    },
    {
        "id": "enemy_crimson_aberration",
        "name": "Crimson Aberration",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a writhing mass of flesh and crimson crystals with too many eyes, grotesque, 1:1, no text",
    },
    {
        "id": "enemy_mirror_doppelganger",
        "name": "Mirror Doppelganger",
        "prompt": "Pixel-art style dark fantasy enemy portrait on black background: a featureless silver humanoid with cracked mirror skin reflecting a distorted hero, unsettling, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for enemy in ENEMIES:
        path = OUT_DIR / f"{enemy['id']}.webp"
        if path.exists():
            print(f"Skipping {enemy['id']} (exists)")
            continue

        print(f"\nGenerating enemy portrait: {enemy['name']}")
        try:
            img = generate_image(enemy["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {enemy['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
