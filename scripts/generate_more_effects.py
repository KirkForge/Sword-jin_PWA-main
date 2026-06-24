#!/usr/bin/env python3
"""
generate_more_effects.py
Batch-generate additional combat effect/spell visual icons for Swordjin.
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
    bg = Image.new("RGB", (size, size), (18, 18, 22))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


EFFECTS = [
    {
        "id": "fx_meteor_strike",
        "name": "Meteor Strike",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a burning orange meteor descending with smoke trail and impact explosion, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_blizzard",
        "name": "Blizzard",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: swirling cyan snowflakes and icy wind vortex, cold area spell, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_chain_lightning",
        "name": "Chain Lightning",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a branching violet lightning bolt jumping between three silhouettes, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_soul_drain",
        "name": "Soul Drain",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a dark red vortex pulling glowing souls from enemies into a central orb, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_holy_nova",
        "name": "Holy Nova",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a golden radial burst of light with floating crosses and sparkles, heal/damage, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_venom_cloud",
        "name": "Venom Cloud",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a green toxic gas cloud with bubbles and skull-shaped fumes, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_earth_spike",
        "name": "Earth Spike",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: jagged brown stone spikes bursting from the ground, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_shadow_lash",
        "name": "Shadow Lash",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a whip of black shadow energy with purple edges, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_blood_moon",
        "name": "Blood Moon",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a red crescent moon dripping blood over a dark battlefield, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_phoenix_rebirth",
        "name": "Phoenix Rebirth",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: an orange phoenix rising from ashes with radiant flames, revive spell, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_void_rift",
        "name": "Void Rift",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a tear in reality showing purple-black void with tentacles emerging, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_golden_torrent",
        "name": "Golden Torrent",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a wave of golden coins and light sweeping forward, fortune spell, centered, game spell icon, 1:1, no text",
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

        print(f"\nGenerating effect: {effect['name']}")
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
