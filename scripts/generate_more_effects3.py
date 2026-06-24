#!/usr/bin/env python3
"""
generate_more_effects3.py
Batch-generate additional combat VFX icons for Swordjin (third wave).
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/effects/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "effects"
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


EFFECTS = [
    {
        "id": "fx_blood_well",
        "name": "Blood Well",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: a bubbling pool of blood with a crimson hand reaching up, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_cinder_swarm",
        "name": "Cinder Swarm",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: a swarm of glowing orange embers forming a spiral, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_frost_nova",
        "name": "Frost Nova",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: a ring of jagged ice crystals exploding outward, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_soul_split",
        "name": "Soul Split",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: a translucent human silhouette splitting into two ghostly forms, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_toxic_mist",
        "name": "Toxic Mist",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: green poisonous vapor with skull shapes drifting inside, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_rune_prison",
        "name": "Rune Prison",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: glowing runic bands forming a cage around a trapped spark, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_solar_flare",
        "name": "Solar Flare",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: a sudden burst of white-gold sunlight with radiating rays, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_void_tendrils",
        "name": "Void Tendrils",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: purple-black tentacles with eyes lashing out from a tear, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_iron_spikes",
        "name": "Iron Spikes",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: jagged metal spikes bursting from the ground in a line, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_wind_wall",
        "name": "Wind Wall",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: a vertical barrier of swirling green wind and leaves, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_gravity_well",
        "name": "Gravity Well",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: a black sphere pulling in arrows and debris, centered, spell effect icon, 1:1, no text",
    },
    {
        "id": "fx_purifying_light",
        "name": "Purifying Light",
        "prompt": "Pixel-art style RPG combat VFX icon on dark background: warm golden light washing away dark shadows and curses, centered, spell effect icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for effect in EFFECTS:
        path = OUT_DIR / f"{effect['id']}.webp"
        if path.exists():
            print(f"Skipping {effect['id']} (exists)")
            continue

        print(f"\nGenerating effect icon: {effect['name']}")
        try:
            img = generate_image(effect["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {effect['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
