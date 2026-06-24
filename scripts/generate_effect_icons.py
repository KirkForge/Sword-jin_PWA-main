#!/usr/bin/env python3
"""
generate_effect_icons.py
Batch-generate VFX/icon art for Swordjin combat effects.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/effects/
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
    bg = Image.new("RGB", (size, size), (20, 20, 25))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


EFFECTS = [
    {
        "id": "fx_sword_slash",
        "name": "Sword Slash",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a silver white sword slash trail with motion blur and spark particles, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_fire_burst",
        "name": "Fire Burst",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: an explosive orange and red fire burst with ember sparks, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_ice_burst",
        "name": "Ice Burst",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a cyan and white ice crystal explosion with frost particles, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_lightning_zap",
        "name": "Lightning Zap",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a jagged violet lightning bolt strike with electric sparks, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_heal_glow",
        "name": "Heal Glow",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a golden glowing cross with soft healing light rays and sparkles, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_poison_cloud",
        "name": "Poison Cloud",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a bubbling green poison gas cloud with skull-shaped vapor, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_blood_splatter",
        "name": "Blood Splatter",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a dramatic red blood splatter with droplets, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_shadow_dash",
        "name": "Shadow Dash",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a smoky black and purple shadow dash trail with afterimages, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_shield_burst",
        "name": "Shield Burst",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a blue translucent shield bubble shattering into light fragments, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_level_up_ring",
        "name": "Level Up Ring",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a golden ring of light rising upward with stars and rays, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_stun_stars",
        "name": "Stun Stars",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: yellow spiral dizzy stars circling above a dazed silhouette, centered, game VFX icon, 1:1, no text",
    },
    {
        "id": "fx_loot_shine",
        "name": "Loot Shine",
        "prompt": "Pixel-art style RPG effect icon on transparent dark background: a golden sparkle burst with coins and gem fragments falling, centered, game VFX icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for fx in EFFECTS:
        path = OUT_DIR / f"{fx['id']}.webp"
        if path.exists():
            print(f"Skipping {fx['id']} (exists)")
            continue

        print(f"\nGenerating effect: {fx['name']}")
        try:
            img = generate_image(fx["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {fx['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
