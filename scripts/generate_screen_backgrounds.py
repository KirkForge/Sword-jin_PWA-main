#!/usr/bin/env python3
"""
generate_screen_backgrounds.py
Batch-generate screen background art for Swordjin menus and overlays.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/screens/
"""

import base64
import os
import re
import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

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


def fit_to_resolution(img: Image.Image) -> Image.Image:
    img.thumbnail(RESOLUTION, Image.LANCZOS)
    bg = Image.new("RGB", RESOLUTION, (10, 10, 15))
    x = (RESOLUTION[0] - img.width) // 2
    y = (RESOLUTION[1] - img.height) // 2
    bg.paste(img, (x, y))
    return bg


def add_vignette_darken(img: Image.Image) -> Image.Image:
    """Add a subtle dark vignette so UI text remains readable."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size
    for i in range(min(w, h) // 2, 0, -4):
        alpha = int(60 * (1 - i / (min(w, h) // 2)))
        draw.ellipse([w // 2 - i, h // 2 - i, w // 2 + i, h // 2 + i], fill=(0, 0, 0, alpha))
    img_rgba = img.convert("RGBA")
    blended = Image.alpha_composite(img_rgba, overlay)
    return blended.convert("RGB")


SCREENS = [
    {
        "name": "chapter_select_bg",
        "prompt": "Dark fantasy menu background: an open leather-bound chapter map spread on a war table, candles burning, small metal figurines representing acts, warm amber light, painterly digital art, 16:9, no text",
    },
    {
        "name": "bestiary_bg",
        "prompt": "Dark fantasy menu background: a dusty bestiary tome open on a wooden stand, ink sketches of monsters in the margins, faint magical lantern light, painterly digital art, 16:9, no text",
    },
    {
        "name": "inventory_bg",
        "prompt": "Dark fantasy menu background: a mercenary's open satchel with weapons, potions, and a rolled map, campfire light outside the tent, painterly digital art, 16:9, no text",
    },
    {
        "name": "shop_bg",
        "prompt": "Dark fantasy menu background: a cluttered merchant stall at night, hanging lanterns, weapon racks, potion bottles, rolled carpets, cozy and mysterious, painterly digital art, 16:9, no text",
    },
    {
        "name": "daily_challenge_bg",
        "prompt": "Dark fantasy menu background: a crimson challenge banner hanging over a dueling pit, stormy sky, crowd silhouettes, dramatic painterly digital art, 16:9, no text",
    },
    {
        "name": "victory_chapter_bg",
        "prompt": "Dark fantasy victory screen background: a battlefield at dawn with raised swords and banners, soft golden light breaking through clouds, triumphant but somber, painterly digital art, 16:9, no text",
    },
    {
        "name": "game_over_bg",
        "prompt": "Dark fantasy defeat screen background: a fallen sword lying in mud and rain, crows in the distance, cold blue-grey atmosphere, painterly digital art, 16:9, no text",
    },
    {
        "name": "settings_bg",
        "prompt": "Dark fantasy menu background: an imperial command tent interior with folded maps, wax seals, a brass compass, and a dim lantern, painterly digital art, 16:9, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for screen in SCREENS:
        path = OUT_DIR / f"{screen['name']}.webp"
        if path.exists():
            print(f"Skipping {screen['name']} (exists)")
            continue

        print(f"\nGenerating screen: {screen['name']}")
        try:
            img = generate_image(screen["prompt"], api_key)
            bg = fit_to_resolution(img)
            bg = add_vignette_darken(bg)
            bg.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {screen['name']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
