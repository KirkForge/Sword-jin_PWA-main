#!/usr/bin/env python3
"""
generate_shop_icons.py
Batch-generate shop/merchant icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/items/ and ui/
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
UI_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "ui"
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


SHOP_ITEMS = [
    {
        "id": "shop_sign",
        "name": "Shop Sign",
        "prompt": "Pixel-art style RPG shop icon on dark background: a hanging wooden sign with a sword and coin emblem, centered, game UI icon, 1:1, no text",
        "out_dir": UI_DIR,
    },
    {
        "id": "shop_merchant",
        "name": "Merchant Portrait",
        "prompt": "Pixel-art style RPG merchant portrait on dark background: a friendly hooded trader with a coin pouch and scales, centered, character icon, 1:1, no text",
        "out_dir": UI_DIR,
    },
    {
        "id": "shop_discount",
        "name": "Discount Coupon",
        "prompt": "Pixel-art style RPG shop icon on dark background: a scroll coupon with a large percent symbol and a gold seal, centered, game item icon, 1:1, no text",
        "out_dir": OUT_DIR,
    },
    {
        "id": "shop_upgrade_hammer",
        "name": "Upgrade Hammer",
        "prompt": "Pixel-art style RPG upgrade icon on dark background: a blacksmith hammer striking an anvil with sparks, centered, game item icon, 1:1, no text",
        "out_dir": OUT_DIR,
    },
    {
        "id": "shop_lucky_charm",
        "name": "Lucky Charm",
        "prompt": "Pixel-art style RPG accessory icon on dark background: a golden four-leaf clover charm on a leather cord, centered, game item icon, 1:1, no text",
        "out_dir": OUT_DIR,
    },
    {
        "id": "shop_contract",
        "name": "Bounty Contract",
        "prompt": "Pixel-art style RPG scroll icon on dark background: an official contract with a red wax seal and a sword symbol, centered, game item icon, 1:1, no text",
        "out_dir": OUT_DIR,
    },
    {
        "id": "shop_gem_pouch",
        "name": "Gem Pouch",
        "prompt": "Pixel-art style RPG item icon on dark background: a small velvet pouch spilling colorful gems, centered, game item icon, 1:1, no text",
        "out_dir": OUT_DIR,
    },
    {
        "id": "shop_healer_band",
        "name": "Healer's Band",
        "prompt": "Pixel-art style RPG accessory icon on dark background: a white cloth armband with a red cross and a soft glow, centered, game item icon, 1:1, no text",
        "out_dir": OUT_DIR,
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    UI_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directories: {OUT_DIR}, {UI_DIR}")

    for item in SHOP_ITEMS:
        out_dir = item["out_dir"]
        path = out_dir / f"{item['id']}.webp"
        if path.exists():
            print(f"Skipping {item['id']} (exists)")
            continue

        print(f"\nGenerating shop icon: {item['name']}")
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
