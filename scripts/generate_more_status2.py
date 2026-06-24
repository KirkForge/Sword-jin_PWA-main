#!/usr/bin/env python3
"""
generate_more_status2.py
Batch-generate additional status effect/buff-debuff icons for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/status/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "status"
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
    bg = Image.new("RGB", (size, size), (20, 20, 24))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


STATUS = [
    {
        "id": "status_frenzied",
        "name": "Frenzied",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a foaming mouth with bared teeth and red speed lines, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_shattered",
        "name": "Shattered",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a broken helmet with cracks and falling shards, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_lifebond",
        "name": "Lifebond",
        "prompt": "Pixel-art style RPG status effect icon on dark background: two red hearts linked by a golden chain, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_withered",
        "name": "Withered",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a dried black hand with falling leaves, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_guided",
        "name": "Guided",
        "prompt": "Pixel-art style RPG status effect icon on dark background: an eye with a beam of golden light pointing the way, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_cursed_blade",
        "name": "Cursed Blade",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a sword dripping black tar with a purple curse aura, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_rejuvenated",
        "name": "Rejuvenated",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a green sprout growing from a heart with sparkles, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_paralyzed",
        "name": "Paralyzed",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a figure frozen in blue ice with yellow electricity arcs, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_hardened",
        "name": "Hardened",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a stony skin texture with cracks and orange core, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_panicked",
        "name": "Panicked",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a wide eye with jagged black lines and cold sweat, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_resonant",
        "name": "Resonant",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a tuning fork vibrating with cyan sound rings, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_burning_soul",
        "name": "Burning Soul",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a blue-white flame inside a ribcage silhouette, centered, debuff icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for status in STATUS:
        path = OUT_DIR / f"{status['id']}.webp"
        if path.exists():
            print(f"Skipping {status['id']} (exists)")
            continue

        print(f"\nGenerating status icon: {status['name']}")
        try:
            img = generate_image(status["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {status['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
