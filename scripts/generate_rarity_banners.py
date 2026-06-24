#!/usr/bin/env python3
"""
generate_rarity_banners.py
Batch-generate rarity banner/tier icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/ui/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "ui"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (128, 32)


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
        "aspect_ratio": "16:9",
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


def fit_banner(img: Image.Image, size: tuple) -> Image.Image:
    target_w, target_h = size
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        new_w = target_w
        new_h = int(target_w / img_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * img_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    bg = Image.new("RGB", (target_w, target_h), (15, 15, 18))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


BANNERS = [
    {
        "id": "rarity_common",
        "name": "Common Banner",
        "prompt": "Pixel-art style RPG rarity banner on dark background: a simple grey iron banner with a plain border, horizontal rectangular shape, centered, game UI element, no text",
    },
    {
        "id": "rarity_uncommon",
        "name": "Uncommon Banner",
        "prompt": "Pixel-art style RPG rarity banner on dark background: a green leaf-textured banner with a thin silver border, horizontal rectangular shape, centered, game UI element, no text",
    },
    {
        "id": "rarity_rare",
        "name": "Rare Banner",
        "prompt": "Pixel-art style RPG rarity banner on dark background: a blue velvet banner with a gold border and subtle gem studs, horizontal rectangular shape, centered, game UI element, no text",
    },
    {
        "id": "rarity_legendary",
        "name": "Legendary Banner",
        "prompt": "Pixel-art style RPG rarity banner on dark background: an ornate golden and orange banner with intricate borders and a crown motif, horizontal rectangular shape, centered, game UI element, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for banner in BANNERS:
        path = OUT_DIR / f"{banner['id']}.webp"
        if path.exists():
            print(f"Skipping {banner['id']} (exists)")
            continue

        print(f"\nGenerating rarity banner: {banner['name']}")
        try:
            img = generate_image(banner["prompt"], api_key)
            fitted = fit_banner(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {banner['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
