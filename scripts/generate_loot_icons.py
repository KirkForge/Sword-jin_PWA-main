#!/usr/bin/env python3
"""
generate_loot_icons.py
Batch-generate additional loot/armor/accessory/material icon art for Swordjin.
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


ITEMS = [
    {
        "id": "iron_shield",
        "name": "Iron Shield",
        "prompt": "Pixel-art style RPG equipment icon on dark background: a round iron shield with a steel boss and leather straps, slightly battle-dented, centered, game item icon, 1:1, no text",
    },
    {
        "id": "steel_helm",
        "name": "Steel Helm",
        "prompt": "Pixel-art style RPG equipment icon on dark background: a closed steel knight helmet with narrow visor slit and gold trim, centered, game item icon, 1:1, no text",
    },
    {
        "id": "leather_boots",
        "name": "Leather Boots",
        "prompt": "Pixel-art style RPG equipment icon on dark background: a pair of worn leather travel boots with steel toe caps, centered, game item icon, 1:1, no text",
    },
    {
        "id": "chainmail_vest",
        "name": "Chainmail Vest",
        "prompt": "Pixel-art style RPG equipment icon on dark background: a folded chainmail vest with iron rings glinting, centered, game item icon, 1:1, no text",
    },
    {
        "id": "shadow_cloak",
        "name": "Shadow Cloak",
        "prompt": "Pixel-art style RPG equipment icon on dark background: a dark hooded cloak with faint purple shadow trim, mysterious, centered, game item icon, 1:1, no text",
    },
    {
        "id": "ruby_ring",
        "name": "Ruby Ring",
        "prompt": "Pixel-art style RPG accessory icon on dark background: a gold signet ring with a glowing ruby inset, centered, game item icon, 1:1, no text",
    },
    {
        "id": "sapphire_amulet",
        "name": "Sapphire Amulet",
        "prompt": "Pixel-art style RPG accessory icon on dark background: a silver amulet with a bright sapphire crystal on a chain, centered, game item icon, 1:1, no text",
    },
    {
        "id": "throwing_knives",
        "name": "Throwing Knives",
        "prompt": "Pixel-art style RPG weapon icon on dark background: three slim throwing knives with black handles stacked in a fan, centered, game item icon, 1:1, no text",
    },
    {
        "id": "explosive_bomb",
        "name": "Explosive Bomb",
        "prompt": "Pixel-art style RPG item icon on dark background: a round black iron bomb with a lit fuse and yellow spark, centered, game item icon, 1:1, no text",
    },
    {
        "id": "antidote_vial",
        "name": "Antidote Vial",
        "prompt": "Pixel-art style RPG item icon on dark background: a small crystal vial with glowing green liquid, cork stopper, centered, game item icon, 1:1, no text",
    },
    {
        "id": "stamina_tonic",
        "name": "Stamina Tonic",
        "prompt": "Pixel-art style RPG item icon on dark background: a brown leather flask with amber liquid and a cork, centered, game item icon, 1:1, no text",
    },
    {
        "id": "relic_bone_shard",
        "name": "Relic Bone Shard",
        "prompt": "Pixel-art style RPG material icon on dark background: a jagged ancient bone shard wrapped in faint spectral mist, centered, game item icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for item in ITEMS:
        path = OUT_DIR / f"{item['id']}.webp"
        if path.exists():
            print(f"Skipping {item['id']} (exists)")
            continue

        print(f"\nGenerating item: {item['name']}")
        try:
            img = generate_image(item["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {item['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
