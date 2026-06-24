#!/usr/bin/env python3
"""
generate_more_status3.py
Batch-generate additional status effect/buff-debuff icons for Swordjin (third wave).
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
        "id": "status_souldrain",
        "name": "Souldrain",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a heart leaking blue soul wisps into a clawed hand, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_mending",
        "name": "Mending",
        "prompt": "Pixel-art style RPG status effect icon on dark background: green stitches weaving together a torn wound with soft light, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_blindsight",
        "name": "Blindsight",
        "prompt": "Pixel-art style RPG status effect icon on dark background: closed eyes surrounded by silver ripples sensing movement, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_rusted",
        "name": "Rusted",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a sword covered in orange rust flakes and corrosion, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_empowered",
        "name": "Empowered",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a flexing arm wreathed in golden sparks and power lines, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_charmed",
        "name": "Charmed",
        "prompt": "Pixel-art style RPG status effect icon on dark background: pink hearts and music notes swirling around a dazed eye, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_unyielding",
        "name": "Unyielding",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a stone shield refusing to crack under a hammer blow, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_infected",
        "name": "Infected",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a green pustule spreading black veins on skin, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_illusion",
        "name": "Illusion",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a translucent figure flickering with rainbow afterimages, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_marked_for_death",
        "name": "Marked for Death",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a red skull target reticle locking onto a silhouette, centered, debuff icon, 1:1, no text",
    },
    {
        "id": "status_resolute",
        "name": "Resolute",
        "prompt": "Pixel-art style RPG status effect icon on dark background: a knight standing firm against a storm with a glowing blue aura, centered, buff icon, 1:1, no text",
    },
    {
        "id": "status_doomed",
        "name": "Doomed",
        "prompt": "Pixel-art style RPG status effect icon on dark background: an hourglass full of black sand with the last grain falling, centered, debuff icon, 1:1, no text",
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
