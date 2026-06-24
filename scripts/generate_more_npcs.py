#!/usr/bin/env python3
"""
generate_more_npcs.py
Batch-generate additional NPC dialogue portraits for Swordjin.
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
        "id": "dark_priest",
        "name": "Dark Priest",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a hooded dark priest wearing a carved bone fang mask, crimson robes, holding a gnarled staff, menacing stillness, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "innkeeper_maya",
        "name": "Innkeeper Maya",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a warm middle-aged innkeeper woman with flour on her apron, kind eyes, holding a mug, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "spirit_guide",
        "name": "Spirit Guide",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a translucent blue spectral guide with gentle glowing eyes and flowing ghostly hair, ethereal, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "imperial_soldier",
        "name": "Imperial Soldier",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a young imperial soldier in simple plate armor with a determined but tired expression, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "ally_warrior_lyra",
        "name": "Lyra the Blade",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a fierce female warrior ally with braided hair, leather armor, scar across her cheek, confident expression, fantasy pixel art, bust shot, centered, no text",
    },
    {
        "id": "crimson_officer",
        "name": "Crimson Fang Officer",
        "prompt": "Pixel-art style RPG dialogue portrait on dark neutral background: a sharp-eyed Crimson Fang officer in red-trimmed black leather armor, cruel smirk, fantasy pixel art, bust shot, centered, no text",
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
