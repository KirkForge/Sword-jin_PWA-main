#!/usr/bin/env python3
"""
generate_material_icons.py
Batch-generate crafting material/resource icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/items/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "items"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (128, 128)


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


def fit_square(img: Image.Image, size: int = 128) -> Image.Image:
    img.thumbnail((size, size), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (20, 20, 25))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


MATERIALS = [
    {
        "id": "mat_iron_ore",
        "name": "Iron Ore",
        "prompt": "Pixel-art style RPG material icon on dark background: a rough chunk of iron ore with metallic grey flecks and rust spots, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_steel_ingot",
        "name": "Steel Ingot",
        "prompt": "Pixel-art style RPG material icon on dark background: a polished rectangular steel ingot with a blue-grey sheen, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_leather",
        "name": "Tough Leather",
        "prompt": "Pixel-art style RPG material icon on dark background: a folded piece of brown leather with stitching and texture, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_silk",
        "name": "Fine Silk",
        "prompt": "Pixel-art style RPG material icon on dark background: a delicate folded silk cloth in deep purple with a subtle shimmer, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_ember_dust",
        "name": "Ember Dust",
        "prompt": "Pixel-art style RPG material icon on dark background: a small pile of glowing orange-red ember dust in a leather pouch, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_frost_shard",
        "name": "Frost Shard",
        "prompt": "Pixel-art style RPG material icon on dark background: a jagged cyan ice shard with frost mist drifting from it, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_shadow_essence",
        "name": "Shadow Essence",
        "prompt": "Pixel-art style RPG material icon on dark background: a swirling ball of black and purple shadow mist in a glass orb, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_gold_bar",
        "name": "Gold Bar",
        "prompt": "Pixel-art style RPG material icon on dark background: a shiny gold bar stamped with a royal seal, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_herb",
        "name": "Medicinal Herb",
        "prompt": "Pixel-art style RPG material icon on dark background: a bundle of green medicinal herbs tied with twine and small white flowers, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "mat_spirit_residue",
        "name": "Spirit Residue",
        "prompt": "Pixel-art style RPG material icon on dark background: faint glowing blue ectoplasmic residue in a small crystal vial, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "gem_sapphire",
        "name": "Sapphire",
        "prompt": "Pixel-art style RPG material icon on dark background: a brilliant blue sapphire cut gem with inner light, centered, game resource icon, 1:1, no text",
    },
    {
        "id": "gem_emerald",
        "name": "Emerald",
        "prompt": "Pixel-art style RPG material icon on dark background: a vivid green emerald cut gem with inner light, centered, game resource icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for mat in MATERIALS:
        path = OUT_DIR / f"{mat['id']}.webp"
        if path.exists():
            print(f"Skipping {mat['id']} (exists)")
            continue

        print(f"\nGenerating material: {mat['name']}")
        try:
            img = generate_image(mat["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {mat['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
