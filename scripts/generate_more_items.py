#!/usr/bin/env python3
"""
generate_more_items.py
Batch-generate additional weapon, armor, and item icons for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/items/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "items"
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


ITEMS = [
    {
        "id": "item_iron_longsword",
        "name": "Iron Longsword",
        "prompt": "Pixel-art style RPG item icon on dark background: a plain but reliable iron longsword with a leather grip, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_crimson_blade",
        "name": "Crimson Blade",
        "prompt": "Pixel-art style RPG item icon on dark background: a wicked curved sword with a blood-red fuller and black hilt, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_ashmont_halberd",
        "name": "Ashmont Halberd",
        "prompt": "Pixel-art style RPG item icon on dark background: a long polearm with an axe blade and spear tip, dark wood shaft, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_void_dagger",
        "name": "Void Dagger",
        "prompt": "Pixel-art style RPG item icon on dark background: a shadowy dagger that seems to absorb light, purple smoke trailing from blade, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_ranger_bow",
        "name": "Ranger's Bow",
        "prompt": "Pixel-art style RPG item icon on dark background: a curved yew bow with green leather grip and silver string, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_tower_shield",
        "name": "Tower Shield",
        "prompt": "Pixel-art style RPG item icon on dark background: a heavy rectangular shield with iron trim and a heraldic crimson tear emblem, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_plate_armor",
        "name": "Knight's Plate",
        "prompt": "Pixel-art style RPG item icon on dark background: a polished steel breastplate with pauldrons and a noble crest, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_hunter_cloak",
        "name": "Hunter's Cloak",
        "prompt": "Pixel-art style RPG item icon on dark background: a weathered green cloak with fur collar and a clasp shaped like a wolf head, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_mystic_robes",
        "name": "Mystic Robes",
        "prompt": "Pixel-art style RPG item icon on dark background: flowing purple and silver ritual robes embroidered with glowing arcane sigils, centered, game equipment icon, 1:1, no text",
    },
    {
        "id": "item_healing_salve",
        "name": "Healing Salve",
        "prompt": "Pixel-art style RPG item icon on dark background: a small ceramic jar of glowing green herbal balm with a leaf label, centered, game consumable icon, 1:1, no text",
    },
    {
        "id": "item_antidote",
        "name": "Antidote Vial",
        "prompt": "Pixel-art style RPG item icon on dark background: a slender glass vial filled with bubbling blue liquid and a cork stopper, centered, game consumable icon, 1:1, no text",
    },
    {
        "id": "item_tear_fragment",
        "name": "Tear Fragment",
        "prompt": "Pixel-art style RPG item icon on dark background: a jagged crystalline shard glowing with inner red light, pulsing softly, centered, game quest item icon, 1:1, no text",
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

        print(f"\nGenerating item icon: {item['name']}")
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
