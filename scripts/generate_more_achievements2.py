#!/usr/bin/env python3
"""
generate_more_achievements2.py
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
        "id": "ach_first_blood",
        "name": "First Blood",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a single crimson drop falling from a sword tip, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_boss_slayer",
        "name": "Boss Slayer",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a broken horned demon skull with a sword through it, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_treasure_hunter",
        "name": "Treasure Hunter",
        "prompt": "Pixel-art style RPG achievement badge on dark background: an open treasure chest overflowing with gold coins and gems, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_perfect_run",
        "name": "Perfect Run",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a flawless golden laurel wreath with a perfect star in the center, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_completionist",
        "name": "Completionist",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a complete jigsaw puzzle glowing with every piece in place, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_speedster",
        "name": "Speedster",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a winged hourglass with motion blur lines behind it, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_iron_will",
        "name": "Iron Will",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a steel anvil struck by lightning, unbroken, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_savior",
        "name": "Savior",
        "prompt": "Pixel-art style RPG achievement badge on dark background: two hands clasped in rescue with a soft white glow, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_duelist",
        "name": "Duelist",
        "prompt": "Pixel-art style RPG achievement badge on dark background: two crossed rapiers with a single rose, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_survivor",
        "name": "Survivor",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a tattered banner still standing on a battlefield hill, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_archmage",
        "name": "Archmage",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a wizard's staff crowned with a blazing spell prism, centered, emblem, 1:1, no text",
    },
    {
        "id": "ach_peacemaker",
        "name": "Peacemaker",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a white dove landing on a sheathed sword, centered, emblem, 1:1, no text",
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
