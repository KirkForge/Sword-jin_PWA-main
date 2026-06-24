#!/usr/bin/env python3
"""
generate_loading_screens.py
Batch-generate loading screen background art for Swordjin.
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
    bg = Image.new("RGB", (target_w, target_h), (10, 10, 12))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


def vignette_darken(img: Image.Image) -> Image.Image:
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pixels = overlay.load()
    center_x, center_y = w / 2.0, h / 2.0
    max_dist = ((center_x) ** 2 + (center_y) ** 2) ** 0.5
    for y in range(h):
        for x in range(w):
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            alpha = int(120 * (dist / max_dist))
            pixels[x, y] = (0, 0, 0, alpha)
    img_rgba = img.convert("RGBA")
    return Image.alpha_composite(img_rgba, overlay).convert("RGB")


LOADING_SCREENS = [
    {
        "id": "loading_ruins",
        "name": "Loading Ruins",
        "prompt": "Cinematic dark fantasy loading screen art 16:9: crumbling ancient ruins at twilight, broken statues and overgrown vines, moody atmosphere, painterly digital art, no text",
    },
    {
        "id": "loading_forest",
        "name": "Loading Forest",
        "prompt": "Cinematic dark fantasy loading screen art 16:9: a misty pine forest with shafts of pale moonlight, mysterious and quiet, painterly digital art, no text",
    },
    {
        "id": "loading_battle",
        "name": "Loading Battle",
        "prompt": "Cinematic dark fantasy loading screen art 16:9: a chaotic battlefield aftermath with smoke, fallen banners, and distant fires, painterly digital art, no text",
    },
    {
        "id": "loading_void",
        "name": "Loading Void",
        "prompt": "Cinematic dark fantasy loading screen art 16:9: swirling purple and black void space with floating stone fragments and distant stars, painterly digital art, no text",
    },
    {
        "id": "loading_camp",
        "name": "Loading Camp",
        "prompt": "Cinematic dark fantasy loading screen art 16:9: a cozy military camp at night with tents, campfires, and soldiers resting, warm glow, painterly digital art, no text",
    },
    {
        "id": "loading_gate",
        "name": "Loading Gate",
        "prompt": "Cinematic dark fantasy loading screen art 16:9: a massive iron fortress gate at dawn with banners and torches, imposing and grand, painterly digital art, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for screen in LOADING_SCREENS:
        path = OUT_DIR / f"{screen['id']}.webp"
        if path.exists():
            print(f"Skipping {screen['id']} (exists)")
            continue

        print(f"\nGenerating loading screen: {screen['name']}")
        try:
            img = generate_image(screen["prompt"], api_key)
            fitted = resize_with_letterbox(img, RESOLUTION)
            darkened = vignette_darken(fitted)
            darkened.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {screen['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
