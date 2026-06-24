#!/usr/bin/env python3
"""
generate_more_status4.py
Batch-generate additional status effect icons for Swordjin (fourth wave).
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
    bg = Image.new("RGB", (size, size), (22, 22, 26))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


STATUSES = [
    {
        "id": "status_ablaze",
        "name": "Ablaze",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a figure silhouetted in roaring orange flames, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_befouled",
        "name": "Befouled",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a green dripping stain corrupting a clean heart, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_blood_rage",
        "name": "Blood Rage",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a snarling warrior face with blood streaming from eyes, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_cocooned",
        "name": "Cocooned",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a figure wrapped in thick spider silk with only glowing eyes visible, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_ensnared",
        "name": "Ensnared",
        "prompt": "Pixel-art style RPG status effect icon on dark background: thorny vines wrapped tightly around struggling legs, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_exposed",
        "name": "Exposed",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a cracked shield with a glowing red target mark behind it, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_frenzy",
        "name": "Frenzy",
        "prompt": "Pixel-art style RPG status effect icon on dark background: crossed bloody axes beneath a berserk red eye, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_hexed",
        "name": "Hexed",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a skull with a purple voodoo pin through one eye socket, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_phased",
        "name": "Phased",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a translucent body partially fading into blue particles, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_rallied",
        "name": "Rallied",
        "prompt": "Pixel-art style RPG status effect icon on dark background: raised swords and a golden sunburst behind a charging silhouette, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_taunted",
        "name": "Taunted",
        "prompt": "Pixel-art style RPG status effect icon on dark background: an enraged face with a red targeting reticle over the eyes, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_vampiric",
        "name": "Vampiric",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a pair of fangs dripping red above a pulsing heart, centered, buff icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for status in STATUSES:
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
