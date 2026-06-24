#!/usr/bin/env python3
"""
generate_more_ui3.py
Batch-generate additional UI panel/button/slot art for Swordjin (third wave).
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
    {"id": "ui_panel_amber", "name": "Amber Panel", "prompt": "Pixel-art style RPG UI horizontal panel border on transparent dark background: an amber-gold frame with warm inner glow and dark center area, centered, game UI texture, no text"},
    {"id": "ui_panel_emerald", "name": "Emerald Panel", "prompt": "Pixel-art style RPG UI horizontal panel border on transparent dark background: an emerald-green frame with thorny vine details and dark center area, centered, game UI texture, no text"},
    {"id": "ui_button_amber", "name": "Amber Button", "prompt": "Pixel-art style RPG UI button on transparent dark background: a rectangular amber button with warm glow and bevel, centered, game UI texture, no text"},
    {"id": "ui_button_emerald", "name": "Emerald Button", "prompt": "Pixel-art style RPG UI button on transparent dark background: a rectangular emerald button with vine trim and bevel, centered, game UI texture, no text"},
    {"id": "ui_button_infernal", "name": "Infernal Button", "prompt": "Pixel-art style RPG UI button on transparent dark background: a rectangular black-red button with ember cracks and bevel, centered, game UI texture, no text"},
    {"id": "ui_slot_crafting", "name": "Crafting Slot", "prompt": "Pixel-art style RPG UI square crafting slot frame on transparent dark background: a dark square socket with hammer-and-anvil etching and inner glow, centered, game UI texture, 1:1, no text"},
    {"id": "ui_slot_blessed", "name": "Blessed Slot", "prompt": "Pixel-art style RPG UI square slot frame on transparent dark background: a dark square socket with golden halo and angelic wing details, centered, game UI texture, 1:1, no text"},
    {"id": "ui_slot_cursed", "name": "Cursed Slot", "prompt": "Pixel-art style RPG UI square slot frame on transparent dark background: a dark square socket with red thorn border and inner shadow, centered, game UI texture, 1:1, no text"},
    {"id": "ui_slider_track", "name": "Slider Track", "prompt": "Pixel-art style RPG UI horizontal track bar on transparent dark background: a metallic grooved track with subtle glow, centered, game UI texture, no text"},
    {"id": "ui_tooltip", "name": "Tooltip Frame", "prompt": "Pixel-art style RPG UI tooltip border on transparent dark background: a small ornate frame with pointed bottom like a speech bubble, dark center, centered, game UI texture, no text"},
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
