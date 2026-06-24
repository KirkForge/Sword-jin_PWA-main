#!/usr/bin/env python3
"""
generate_more_achievements.py
Batch-generate additional achievement badge icons for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/achievements/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "achievements"
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
    bg = Image.new("RGB", (size, size), (20, 20, 25))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


BADGES = [
    {
        "id": "ach_first_step",
        "name": "First Step",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a single footprint glowing golden on a stone path, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_veteran",
        "name": "Veteran",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a weathered iron helmet with many battle scars and a faded cape, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_master_of_arms",
        "name": "Master of Arms",
        "prompt": "Pixel-art style RPG achievement badge on dark background: crossed sword, axe, and spear forming a weapon master's crest, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_untouchable",
        "name": "Untouchable",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a translucent dodge shadow silhouette with a perfect circular guard aura, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_lorekeeper",
        "name": "Lorekeeper",
        "prompt": "Pixel-art style RPG achievement badge on dark background: an open glowing book with quill and floating runes, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_philanthropist",
        "name": "Philanthropist",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a merchant's hand giving a coin to another hand with a heart symbol, centered, emblem, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for badge in BADGES:
        path = OUT_DIR / f"{badge['id']}.webp"
        if path.exists():
            print(f"Skipping {badge['id']} (exists)")
            continue

        print(f"\nGenerating achievement badge: {badge['name']}")
        try:
            img = generate_image(badge["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {badge['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
