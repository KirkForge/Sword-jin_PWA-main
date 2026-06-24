#!/usr/bin/env python3
"""
generate_weapon_icons.py
Batch-generate weapon/item icon art for Swordjin loot and inventory.
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
        "id": "iron_longsword",
        "name": "Iron Longsword",
        "prompt": "Pixel-art style RPG weapon icon on transparent moody background: a plain iron longsword with a leather-wrapped hilt, simple crossguard, slightly worn blade, centered, game item icon, 1:1, no text",
    },
    {
        "id": "merchants_dirk",
        "name": "Merchant's Dirk",
        "prompt": "Pixel-art style RPG weapon icon on transparent moody background: a slim merchant's dirk with a brass pommel, sharp point, travel-worn leather grip, centered, game item icon, 1:1, no text",
    },
    {
        "id": "fang_saber",
        "name": "Fang Saber",
        "prompt": "Pixel-art style RPG weapon icon on transparent moody background: a curved Crimson Fang saber with a serrated edge and red leather hilt, centered, game item icon, 1:1, no text",
    },
    {
        "id": "ruin_bastard_sword",
        "name": "Ruin Bastard Sword",
        "prompt": "Pixel-art style RPG weapon icon on transparent moody background: a heavy bastard sword with a blackened blade and faint red runes, centered, game item icon, 1:1, no text",
    },
    {
        "id": "wraith_blade",
        "name": "Wraith Blade",
        "prompt": "Pixel-art style RPG weapon icon on transparent moody background: a spectral sword made of translucent blue spirit metal, ghostly glow, centered, game item icon, 1:1, no text",
    },
    {
        "id": "imperial_glaive",
        "name": "Imperial Glaive",
        "prompt": "Pixel-art style RPG weapon icon on transparent moody background: an imperial glaive with a long curved blade and gold-trimmed shaft, centered, game item icon, 1:1, no text",
    },
    {
        "id": "tower_maul",
        "name": "Tower Maul",
        "prompt": "Pixel-art style RPG weapon icon on transparent moody background: a massive iron maul with obsidian studs and a worn haft, centered, game item icon, 1:1, no text",
    },
    {
        "id": "sword_of_ruin",
        "name": "Sword of Ruin",
        "prompt": "Pixel-art style RPG legendary weapon icon on transparent moody background: the cursed Sword of Ruin, black blade with a crimson core, ornate guard, ominous aura, centered, game item icon, 1:1, no text",
    },
    {
        "id": "potion_health",
        "name": "Health Potion",
        "prompt": "Pixel-art style RPG item icon on transparent moody background: a round glass flask filled with glowing red health potion, cork stopper, centered, game item icon, 1:1, no text",
    },
    {
        "id": "potion_mana",
        "name": "Mana Potion",
        "prompt": "Pixel-art style RPG item icon on transparent moody background: a crystal vial filled with swirling blue mana potion, silver cap, centered, game item icon, 1:1, no text",
    },
    {
        "id": "gate_key",
        "name": "Gate Key",
        "prompt": "Pixel-art style RPG item icon on transparent moody background: a heavy iron skeleton key with a worn crest, faint magical glint, centered, game item icon, 1:1, no text",
    },
    {
        "id": "loot_gem_ruby",
        "name": "Ruby Gem",
        "prompt": "Pixel-art style RPG item icon on transparent moody background: a faceted ruby gem glowing with inner fire, centered, game item icon, 1:1, no text",
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
