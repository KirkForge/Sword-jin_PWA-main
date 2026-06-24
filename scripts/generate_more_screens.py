#!/usr/bin/env python3
"""
generate_more_screens.py
Batch-generate additional menu/loading screen background art for Swordjin.
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


def resize_with_letterbox(img: Image.Image, target: tuple) -> Image.Image:
    target_w, target_h = target
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        new_w = target_w
        new_h = int(target_w / img_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * img_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    bg = Image.new("RGB", (target_w, target_h), (6, 6, 8))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


SCREENS = [
    {
        "id": "screen_daily_alt",
        "name": "Daily Challenge Alt",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a glowing daily quest stone monument at twilight with rotating runes, moody and epic, painterly digital art, no text",
    },
    {
        "id": "screen_shop",
        "name": "Shop Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a cluttered merchant wagon in a torchlit underground bazaar, warm and mysterious, painterly digital art, no text",
    },
    {
        "id": "screen_bestiary",
        "name": "Bestiary Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: an old monster hunter's study with sketches, claws and trophies on stone walls, candlelit, painterly digital art, no text",
    },
    {
        "id": "screen_achievements",
        "name": "Achievements Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a hall of honored banners and golden trophies under shafts of light, grand and solemn, painterly digital art, no text",
    },
    {
        "id": "screen_settings",
        "name": "Settings Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a quiet camp at night with a small fire, equipment laid out, calm atmosphere, painterly digital art, no text",
    },
    {
        "id": "screen_gameover_alt",
        "name": "Game Over Alt",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a fallen sword in grey ash with a dark stormy sky, somber defeat mood, painterly digital art, no text",
    },
    {
        "id": "screen_victory_alt",
        "name": "Victory Alt",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a sun breaking through clouds over a reclaimed battlefield, hopeful victory mood, painterly digital art, no text",
    },
    {
        "id": "screen_map",
        "name": "Map Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: an aged parchment map spread on a wooden table with compass and dagger, adventure planning mood, painterly digital art, no text",
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

        print(f"\nGenerating screen: {screen['name']}")
        try:
            img = generate_image(screen["prompt"], api_key)
            fitted = resize_with_letterbox(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {screen['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
