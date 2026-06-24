#!/usr/bin/env python3
"""
generate_more_achievements6.py
Batch-generate additional achievement badge icons for Swordjin (sixth wave).
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
    bg = Image.new("RGB", (size, size), (25, 20, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


ACHIEVEMENTS = [
    {"id": "ach_aspect_slayer", "name": "Aspect Slayer", "prompt": "Pixel-art style RPG achievement badge on dark background: a shattered magical aspect symbol with a sword thrust through it, centered, badge icon, 1:1, no text"},
    {"id": "ach_chain_breaker", "name": "Chain Breaker", "prompt": "Pixel-art style RPG achievement badge on dark background: heavy chains snapping apart with sparks, centered, badge icon, 1:1, no text"},
    {"id": "ach_crimson_scholar", "name": "Crimson Scholar", "prompt": "Pixel-art style RPG achievement badge on dark background: an open book with bloodstained pages and a glowing rune, centered, badge icon, 1:1, no text"},
    {"id": "ach_daily_champion", "name": "Daily Champion", "prompt": "Pixel-art style RPG achievement badge on dark background: a calendar page with a golden laurel and crossed swords, centered, badge icon, 1:1, no text"},
    {"id": "ach_enduring_flame", "name": "Enduring Flame", "prompt": "Pixel-art style RPG achievement badge on dark background: a small candle flame refusing to go out in a hurricane wind, centered, badge icon, 1:1, no text"},
    {"id": "ach_faction_favored", "name": "Faction Favored", "prompt": "Pixel-art style RPG achievement badge on dark background: three faction banners bowing toward a single raised fist, centered, badge icon, 1:1, no text"},
    {"id": "ach_heart_of_ashmont", "name": "Heart of Ashmont", "prompt": "Pixel-art style RPG achievement badge on dark background: a heart-shaped medallion made of ash and embers, centered, badge icon, 1:1, no text"},
    {"id": "ach_legion_diplomat", "name": "Legion Diplomat", "prompt": "Pixel-art style RPG achievement badge on dark background: a spectral hand and a living hand shaking above a banner, centered, badge icon, 1:1, no text"},
    {"id": "ach_mirror_breaker", "name": "Mirror Breaker", "prompt": "Pixel-art style RPG achievement badge on dark background: a shattered mirror with a single eye visible in the broken glass, centered, badge icon, 1:1, no text"},
    {"id": "ach_no_kings", "name": "No Kings", "prompt": "Pixel-art style RPG achievement badge on dark background: a crown broken in half on a stone floor with a boot nearby, centered, badge icon, 1:1, no text"},
    {"id": "ach_siren_silenced", "name": "Siren Silenced", "prompt": "Pixel-art style RPG achievement badge on dark background: a severed harp string with a ghostly mouth closed forever, centered, badge icon, 1:1, no text"},
    {"id": "ach_wraith_binder", "name": "Wraith Binder", "prompt": "Pixel-art style RPG achievement badge on dark background: a glowing chain binding three writhing wraiths, centered, badge icon, 1:1, no text"},
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for ach in ACHIEVEMENTS:
        path = OUT_DIR / f"{ach['id']}.webp"
        if path.exists():
            print(f"Skipping {ach['id']} (exists)")
            continue
        print(f"\nGenerating achievement: {ach['name']}")
        try:
            img = generate_image(ach["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {ach['id']}: {e}", file=sys.stderr)
            continue
        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
