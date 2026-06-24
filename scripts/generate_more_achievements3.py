#!/usr/bin/env python3
"""
generate_more_achievements3.py
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
    bg = Image.new("RGB", (size, size), (25, 20, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


ACHIEVEMENTS = [
    {
        "id": "ach_collector",
        "name": "Collector",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a golden treasure chest overflowing with gems and artifacts, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_unbroken",
        "name": "Unbroken",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a steel shield with no scratches glowing with inner light, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_lorekeeper",
        "name": "Lorekeeper",
        "prompt": "Pixel-art style RPG achievement badge on dark background: an open ancient book with floating runes and a quill, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_shadow_walker",
        "name": "Shadow Walker",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a hooded figure fading into black mist with one glowing eye, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_dragonslayer",
        "name": "Dragonslayer",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a crossed sword and dragon fang with crimson blood, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_oathkeeper",
        "name": "Oathkeeper",
        "prompt": "Pixel-art style RPG achievement badge on dark background: two clasped hands bound by a golden chain of honor, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_nomad",
        "name": "Nomad",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a worn walking boot leaving a glowing footprint on a road, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_philanthropist",
        "name": "Philanthropist",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a hand giving a glowing gold coin to another hand, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_ascetic",
        "name": "Ascetic",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a simple wooden bowl and staff on a bare mountain peak, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_crimson_scar",
        "name": "Crimson Scar",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a jagged red scar shaped like a tear on dark skin, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_forgemaster",
        "name": "Forgemaster",
        "prompt": "Pixel-art style RPG achievement badge on dark background: an anvil with a hammer striking sparks and molten runes, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_void_touched",
        "name": "Void Touched",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a hand reaching toward a purple-black star with tiny eyes, centered, badge icon, 1:1, no text",
    },
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
