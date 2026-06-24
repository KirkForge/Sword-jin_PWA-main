#!/usr/bin/env python3
"""
generate_npc_portraits.py
Batch-generate NPC/dialogue portrait art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/npcs/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "npcs"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (256, 256)


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


def fit_square(img: Image.Image, size: int = 256) -> Image.Image:
    img.thumbnail((size, size), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (15, 15, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


NPCS = [
    {
        "id": "merchant_ernest",
        "name": "Merchant Ernest",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a friendly middle-aged traveling merchant with a wide brimmed hat, warm smile, sack of goods over shoulder, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "captain_soren",
        "name": "Captain Soren",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a stern bearded imperial captain in plate armor, scar over one eye, stern expression, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "priestess_mira",
        "name": "Priestess Mira",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a serene priestess with silver hair, soft glowing eyes, white and blue robes, gentle smile, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "berserker_korg",
        "name": "Berserker Korg",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a muscular scarred berserker with wild red hair, crude iron armor, mad grin, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "spymaster_vesh",
        "name": "Spymaster Vesh",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a hooded rogue spymaster with a half-mask, sharp eyes, dark leathers, mysterious, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "wraith_king",
        "name": "Wraith King",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a terrifying spectral wraith king with a crown of black iron, hollow glowing eyes, ghostly blue aura, menacing, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "blacksmith_gurn",
        "name": "Blacksmith Gurn",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a burly dwarf-like blacksmith with soot-stained apron, muscular arms crossed, friendly gruff expression, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "scholar_yenn",
        "name": "Scholar Yenn",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: an elderly scholar with spectacles, long grey beard, scroll and quill in hand, wise expression, fantasy pixel art, bust shot, centered, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for npc in NPCS:
        path = OUT_DIR / f"{npc['id']}.webp"
        if path.exists():
            print(f"Skipping {npc['id']} (exists)")
            continue

        print(f"\nGenerating NPC portrait: {npc['name']}")
        try:
            img = generate_image(npc["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {npc['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
