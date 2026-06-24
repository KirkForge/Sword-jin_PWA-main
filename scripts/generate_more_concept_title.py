#!/usr/bin/env python3
"""
generate_more_concept_title.py
Batch-generate additional title screen concept/key art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/concept/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "concept"
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
    bg = Image.new("RGB", (target_w, target_h), (8, 8, 12))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


SCENES = [
    {
        "id": "title_forgotten_hero",
        "name": "Forgotten Hero",
        "prompt": "Cinematic pixel-art fantasy key art, 16:9, dark muted palette: a lone sword-wielding hero kneeling in rain before a field of rusted blades and broken banners, dramatic back-light, no text",
    },
    {
        "id": "title_moonlit_ruins",
        "name": "Moonlit Ruins",
        "prompt": "Cinematic pixel-art fantasy key art, 16:9, dark muted palette: ancient ruins bathed in pale moonlight, a lone figure standing on a crumbling arch, fog and drifting petals, no text",
    },
    {
        "id": "title_dragon_skull",
        "name": "Dragon Skull Gate",
        "prompt": "Cinematic pixel-art fantasy key art, 16:9, dark muted palette: a massive dragon skull forming a gateway into a volcanic valley, ember particles, silhouette of a swordsman, no text",
    },
    {
        "id": "title_last_campfire",
        "name": "Last Campfire",
        "prompt": "Cinematic pixel-art fantasy key art, 16:9, warm muted palette: a small campfire in a dark forest clearing with heroes resting and weapons propped nearby, cozy yet ominous, no text",
    },
    {
        "id": "title_throne_of_blades",
        "name": "Throne of Blades",
        "prompt": "Cinematic pixel-art fantasy key art, 16:9, dark muted palette: a throne made of swords in a vast hall, a shadowy usurper seated upon it, torchlight, no text",
    },
    {
        "id": "title_sunrise_victory",
        "name": "Sunrise Victory",
        "prompt": "Cinematic pixel-art fantasy key art, 16:9, warm golden palette: a warrior raising a sword at sunrise on a hilltop, defeated enemies below, hopeful and epic, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for scene in SCENES:
        path = OUT_DIR / f"{scene['id']}.webp"
        if path.exists():
            print(f"Skipping {scene['id']} (exists)")
            continue

        print(f"\nGenerating concept art: {scene['name']}")
        try:
            img = generate_image(scene["prompt"], api_key)
            fitted = fit_16_9(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {scene['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
