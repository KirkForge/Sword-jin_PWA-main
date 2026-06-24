#!/usr/bin/env python3
"""
generate_currency_icons.py
Batch-generate currency/resource pile icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/items/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "items"
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


CURRENCIES = [
    {
        "id": "gold_pile_small",
        "name": "Small Gold Pile",
        "prompt": "Pixel-art style RPG currency icon on dark background: a small pile of shiny gold coins with a few scattered around, centered, game item icon, 1:1, no text",
    },
    {
        "id": "gold_pile_large",
        "name": "Large Gold Pile",
        "prompt": "Pixel-art style RPG currency icon on dark background: a large heap of glittering gold coins with gems peeking through, centered, game item icon, 1:1, no text",
    },
    {
        "id": "token_daily",
        "name": "Daily Token",
        "prompt": "Pixel-art style RPG currency icon on dark background: a bronze sun-shaped daily challenge token with a sword emblem, centered, game item icon, 1:1, no text",
    },
    {
        "id": "token_achievement",
        "name": "Achievement Token",
        "prompt": "Pixel-art style RPG currency icon on dark background: a silver laurel wreath token with a star in the center, centered, game item icon, 1:1, no text",
    },
    {
        "id": "chest_common",
        "name": "Common Chest",
        "prompt": "Pixel-art style RPG chest icon on dark background: a simple wooden chest with iron bands, closed, centered, game item icon, 1:1, no text",
    },
    {
        "id": "chest_rare",
        "name": "Rare Chest",
        "prompt": "Pixel-art style RPG chest icon on dark background: an ornate blue and silver chest with glowing edges, closed, centered, game item icon, 1:1, no text",
    },
    {
        "id": "chest_legendary",
        "name": "Legendary Chest",
        "prompt": "Pixel-art style RPG chest icon on dark background: a majestic golden chest with ruby inlays and an ethereal glow, closed, centered, game item icon, 1:1, no text",
    },
    {
        "id": "key_boss",
        "name": "Boss Key",
        "prompt": "Pixel-art style RPG key icon on dark background: an ornate black iron key with a skull-shaped bow and red gem, centered, game item icon, 1:1, no text",
    },
    {
        "id": "tome_wisdom",
        "name": "Tome of Wisdom",
        "prompt": "Pixel-art style RPG item icon on dark background: an ancient leather-bound tome with glowing arcane runes on the cover, centered, game item icon, 1:1, no text",
    },
    {
        "id": "map_fragment",
        "name": "Map Fragment",
        "prompt": "Pixel-art style RPG item icon on dark background: a torn piece of old parchment map with inked roads and a red X, centered, game item icon, 1:1, no text",
    },
    {
        "id": "medal_honor",
        "name": "Medal of Honor",
        "prompt": "Pixel-art style RPG item icon on dark background: a bronze military medal with a ribbon and crossed swords, centered, game item icon, 1:1, no text",
    },
    {
        "id": "crown_ruins",
        "name": "Ruined Crown",
        "prompt": "Pixel-art style RPG item icon on dark background: a broken ancient crown with missing jewels and cracks, centered, game item icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for item in CURRENCIES:
        path = OUT_DIR / f"{item['id']}.webp"
        if path.exists():
            print(f"Skipping {item['id']} (exists)")
            continue

        print(f"\nGenerating currency: {item['name']}")
        try:
            img = generate_image(item["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {item['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
