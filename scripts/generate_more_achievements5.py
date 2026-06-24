#!/usr/bin/env python3
"""
generate_more_achievements5.py
Batch-generate additional achievement badge icons for Swordjin (fifth wave).
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
        "id": "ach_abyss_diver",
        "name": "Abyss Diver",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a helmeted figure rappelling into a glowing abyss, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_bane_of_undead",
        "name": "Bane of Undead",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a skull pierced by a silver nail surrounded by holy light, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_blood_oath",
        "name": "Blood Oath",
        "prompt": "Pixel-art style RPG achievement badge on dark background: two hands clasped while blood drips into a shared chalice, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_crimson_ledger",
        "name": "Crimson Ledger",
        "prompt": "Pixel-art style RPG achievement badge on dark background: an open ledger with names crossed out in red ink, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_faithless",
        "name": "Faithless",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a shattered temple icon with a crescent moon behind it, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_fang_lord",
        "name": "Fang Lord",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a crown made of fangs and bone resting on a blood puddle, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_ghost_legionnaire",
        "name": "Ghost Legionnaire",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a spectral soldier saluting with a translucent blue blade, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_harvest_of_ash",
        "name": "Harvest of Ash",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a scythe sweeping through grey ash to reveal glowing seeds, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_moonlit_slayer",
        "name": "Moonlit Slayer",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a dagger silhouetted against a full moon with a single drop of blood, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_oathbreaker",
        "name": "Oathbreaker",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a snapped oath ring with black smoke rising from the pieces, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_scar_warden",
        "name": "Scar Warden",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a shield embossed with a jagged scar glowing with protective light, centered, badge icon, 1:1, no text",
    },
    {
        "id": "ach_void_touched",
        "name": "Void Touched",
        "prompt": "Pixel-art style RPG achievement badge on dark background: a hand reaching into a swirling purple-black void rift, centered, badge icon, 1:1, no text",
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
