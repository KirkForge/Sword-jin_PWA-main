#!/usr/bin/env python3
"""
generate_more_screens2.py
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
        "id": "screen_title_alt",
        "name": "Title Alt",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a battered hero standing before a vast crimson tear in the sky, epic scale, painterly digital art, no text",
    },
    {
        "id": "screen_chapter_select",
        "name": "Chapter Select",
        "prompt": "Cinematic dark fantasy game menu background 16:9: an ancient stone map table with glowing chapter markers floating above it, painterly digital art, no text",
    },
    {
        "id": "screen_inventory",
        "name": "Inventory Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: an adventurer's pack spread open by campfire light with weapons, potions and maps, painterly digital art, no text",
    },
    {
        "id": "screen_camp",
        "name": "Camp Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a party resting around a campfire in a misty forest, warm and tense, painterly digital art, no text",
    },
    {
        "id": "screen_class_select",
        "name": "Class Select",
        "prompt": "Cinematic dark fantasy game menu background 16:9: three shadowy figures representing warrior, mage and rogue standing in a torchlit hall, painterly digital art, no text",
    },
    {
        "id": "screen_faction",
        "name": "Faction Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: three banners of rival houses hanging in a war tent with maps and daggers, painterly digital art, no text",
    },
    {
        "id": "screen_ritual",
        "name": "Ritual Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a candlelit ritual circle with floating runes and bound grimoires, painterly digital art, no text",
    },
    {
        "id": "screen_memory_lane",
        "name": "Memory Lane",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a corridor of floating memory crystals showing past victories and defeats, painterly digital art, no text",
    },
    {
        "id": "screen_blacksmith",
        "name": "Blacksmith Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a cluttered blacksmith workshop with glowing forge, hammers and half-finished armor, painterly digital art, no text",
    },
    {
        "id": "screen_temple",
        "name": "Temple Screen",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a candlelit temple interior with offerings, stained glass and silent robed figures, painterly digital art, no text",
    },
    {
        "id": "screen_tavern_alt",
        "name": "Tavern Alt",
        "prompt": "Cinematic dark fantasy game menu background 16:9: a cozy tavern interior with patrons, mugs, and a bard playing by a warm hearth, painterly digital art, no text",
    },
    {
        "id": "screen_void_menu",
        "name": "Void Menu",
        "prompt": "Cinematic dark fantasy game menu background 16:9: an impossible floating platform in a purple-black void with distant alien structures, painterly digital art, no text",
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
