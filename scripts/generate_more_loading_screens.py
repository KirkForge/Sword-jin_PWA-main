#!/usr/bin/env python3
"""
generate_more_loading_screens.py
Batch-generate additional loading screen backgrounds for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/screens/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "screens"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (640, 360)


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


def fit_16_9(img: Image.Image, size: tuple) -> Image.Image:
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
    bg = Image.new("RGB", (target_w, target_h), (10, 10, 14))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


SCREENS = [
    {
        "id": "loading_mountain",
        "name": "Mountain Pass Loading",
        "prompt": "Pixel-art style fantasy RPG loading screen background, 16:9: a treacherous snowy mountain pass with ancient stone bridges and distant ruins, muted colors, atmospheric, no text",
    },
    {
        "id": "loading_swamp",
        "name": "Swamp Loading",
        "prompt": "Pixel-art style fantasy RPG loading screen background, 16:9: a misty cursed swamp with gnarled trees, floating will-o-wisps, and rotting wooden docks, muted colors, atmospheric, no text",
    },
    {
        "id": "loading_castle",
        "name": "Castle Siege Loading",
        "prompt": "Pixel-art style fantasy RPG loading screen background, 16:9: a massive besieged castle with banners, catapults, and stormy skies, muted colors, atmospheric, no text",
    },
    {
        "id": "loading_arena",
        "name": "Arena Loading",
        "prompt": "Pixel-art style fantasy RPG loading screen background, 16:9: an ancient gladiator arena with cracked marble, bloodstains, and towering spectator ruins, muted colors, atmospheric, no text",
    },
    {
        "id": "loading_void_gate",
        "name": "Void Gate Loading",
        "prompt": "Pixel-art style fantasy RPG loading screen background, 16:9: a swirling purple void gate inside a ruined temple, dark cosmic colors, ethereal, no text",
    },
    {
        "id": "loading_treasure",
        "name": "Treasure Vault Loading",
        "prompt": "Pixel-art style fantasy RPG loading screen background, 16:9: a hidden treasure vault filled with gold, weapons, and glowing relics, warm colors, atmospheric, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for screen in SCREENS:
        path = OUT_DIR / f"{screen['id']}.webp"
        if path.exists():
            print(f"Skipping {screen['id']} (exists)")
            continue

        print(f"\nGenerating loading screen: {screen['name']}")
        try:
            img = generate_image(screen["prompt"], api_key)
            fitted = fit_16_9(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {screen['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
