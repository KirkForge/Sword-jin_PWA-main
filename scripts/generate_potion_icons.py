#!/usr/bin/env python3
"""
generate_potion_icons.py
Batch-generate potion and consumable item icon art for Swordjin.
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


POTIONS = [
    {
        "id": "potion_greater_health",
        "name": "Greater Health Potion",
        "prompt": "Pixel-art style RPG item icon on dark background: a large ornate crystal flask filled with glowing crimson red health potion, golden stopper, centered, game item icon, 1:1, no text",
    },
    {
        "id": "potion_greater_mana",
        "name": "Greater Mana Potion",
        "prompt": "Pixel-art style RPG item icon on dark background: a tall arcane vial filled with swirling deep blue mana potion, silver runes on glass, centered, game item icon, 1:1, no text",
    },
    {
        "id": "potion_speed",
        "name": "Speed Elixir",
        "prompt": "Pixel-art style RPG item icon on dark background: a slim golden flask with amber liquid and motion streaks on the label, centered, game item icon, 1:1, no text",
    },
    {
        "id": "potion_strength",
        "name": "Strength Tonic",
        "prompt": "Pixel-art style RPG item icon on dark background: a bulky iron flask filled with glowing orange-red liquid and a fist symbol, centered, game item icon, 1:1, no text",
    },
    {
        "id": "potion_resistance",
        "name": "Ironhide Brew",
        "prompt": "Pixel-art style RPG item icon on dark background: a stone-grey flask with a shield emblem and metallic liquid, centered, game item icon, 1:1, no text",
    },
    {
        "id": "potion_luck",
        "name": "Gambler's Draught",
        "prompt": "Pixel-art style RPG item icon on dark background: a shimmering rainbow-colored potion in a triangular bottle with a four-leaf clover charm, centered, game item icon, 1:1, no text",
    },
    {
        "id": "scroll_fire",
        "name": "Fire Scroll",
        "prompt": "Pixel-art style RPG item icon on dark background: an ancient rolled parchment scroll sealed with red wax and a flame rune, centered, game item icon, 1:1, no text",
    },
    {
        "id": "scroll_ice",
        "name": "Ice Scroll",
        "prompt": "Pixel-art style RPG item icon on dark background: an ancient rolled parchment scroll sealed with blue wax and a snowflake rune, centered, game item icon, 1:1, no text",
    },
    {
        "id": "scroll_lightning",
        "name": "Lightning Scroll",
        "prompt": "Pixel-art style RPG item icon on dark background: an ancient rolled parchment scroll sealed with purple wax and a lightning rune, centered, game item icon, 1:1, no text",
    },
    {
        "id": "food_rations",
        "name": "Travel Rations",
        "prompt": "Pixel-art style RPG item icon on dark background: a simple cloth sack with bread, cheese, and dried meat tied with twine, centered, game item icon, 1:1, no text",
    },
    {
        "id": "bandage",
        "name": "Bandages",
        "prompt": "Pixel-art style RPG item icon on dark background: a clean white rolled cloth bandage with a small red cross, centered, game item icon, 1:1, no text",
    },
    {
        "id": "torch",
        "name": "Torch",
        "prompt": "Pixel-art style RPG item icon on dark background: a wooden torch with a bright orange flame and drifting sparks, centered, game item icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for item in POTIONS:
        path = OUT_DIR / f"{item['id']}.webp"
        if path.exists():
            print(f"Skipping {item['id']} (exists)")
            continue

        print(f"\nGenerating potion: {item['name']}")
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
