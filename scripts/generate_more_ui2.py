#!/usr/bin/env python3
"""
generate_more_ui2.py
Batch-generate additional UI panel/button/slot art for Swordjin (second wave).
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/ui/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "ui"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (320, 64)


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
        "aspect_ratio": "16:9",
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


def fit_horizontal_bar(img: Image.Image, size: tuple) -> Image.Image:
    target_w, target_h = size
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        new_w = target_w
        new_h = int(target_w / img_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * img_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    bg = Image.new("RGB", (target_w, target_h), (15, 15, 18))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


FRAMES = [
    {
        "id": "ui_panel_blood",
        "name": "Blood Panel",
        "prompt": "Pixel-art style RPG UI horizontal panel border on transparent dark background: a deep crimson frame with pulsing vein-like borders and dark center area, centered, game UI texture, no text",
    },
    {
        "id": "ui_panel_frost",
        "name": "Frost Panel",
        "prompt": "Pixel-art style RPG UI horizontal panel border on transparent dark background: an icy blue frame with frost patterns and a dark center area, centered, game UI texture, no text",
    },
    {
        "id": "ui_button_blood",
        "name": "Blood Button",
        "prompt": "Pixel-art style RPG UI button on transparent dark background: a rectangular dark-red button with subtle pulsing glow and bevel, centered, game UI texture, no text",
    },
    {
        "id": "ui_button_frost",
        "name": "Frost Button",
        "prompt": "Pixel-art style RPG UI button on transparent dark background: a rectangular pale-blue button with frost trim and bevel, centered, game UI texture, no text",
    },
    {
        "id": "ui_button_void",
        "name": "Void Button",
        "prompt": "Pixel-art style RPG UI button on transparent dark background: a rectangular black button with purple runic glow and bevel, centered, game UI texture, no text",
    },
    {
        "id": "ui_slot_ability",
        "name": "Ability Slot",
        "prompt": "Pixel-art style RPG UI square ability slot frame on transparent dark background: a dark square socket with glowing inner rune ring, centered, game UI texture, 1:1, no text",
    },
    {
        "id": "ui_slot_rune",
        "name": "Rune Slot",
        "prompt": "Pixel-art style RPG UI square rune slot frame on transparent dark background: a stone-carved square socket with faint orange rune border, centered, game UI texture, 1:1, no text",
    },
    {
        "id": "ui_tab_active",
        "name": "Active Tab",
        "prompt": "Pixel-art style RPG UI horizontal tab on transparent dark background: an active tab with glowing golden top border and dark body, centered, game UI texture, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for frame in FRAMES:
        is_square = "slot" in frame["id"]
        size = (128, 128) if is_square else RESOLUTION
        path = OUT_DIR / f"{frame['id']}.webp"
        if path.exists():
            print(f"Skipping {frame['id']} (exists)")
            continue

        print(f"\nGenerating UI frame: {frame['name']}")
        try:
            img = generate_image(frame["prompt"], api_key)
            if is_square:
                img.thumbnail(size, Image.LANCZOS)
                fitted = Image.new("RGB", size, (15, 15, 18))
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                fitted.paste(img, (x, y))
            else:
                fitted = fit_horizontal_bar(img, size)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {frame['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
