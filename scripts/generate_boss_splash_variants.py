#!/usr/bin/env python3
"""
generate_boss_splash_variants.py
Batch-generate additional boss splash art variants for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/boss_splash/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "boss_splash"
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


BOSSES = [
    {
        "id": "boss_skeleton_captain_alt",
        "name": "Skeleton Captain Alt",
        "prompt": "Cinematic pixel-art fantasy boss splash art, 16:9, dark muted palette: an armored skeleton captain with a tower shield and rusted broadsword, green eye flames, stormy battlefield, no text",
    },
    {
        "id": "boss_wraith_king_alt",
        "name": "Wraith King Alt",
        "prompt": "Cinematic pixel-art fantasy boss splash art, 16:9, dark muted palette: a tall wraith king in a tattered crown cloak, ghostly blade, swirling souls, no text",
    },
    {
        "id": "boss_bandit_king_alt",
        "name": "Bandit King Alt",
        "prompt": "Cinematic pixel-art fantasy boss splash art, 16:9, warm muted palette: a muscular bandit king with a spiked club and fur cloak, roaring in a forest camp, no text",
    },
    {
        "id": "boss_necromancer_alt",
        "name": "Necromancer Alt",
        "prompt": "Cinematic pixel-art fantasy boss splash art, 16:9, dark muted palette: a hooded necromancer raising skeletons from a ritual circle, purple magic, no text",
    },
    {
        "id": "boss_golem_alt",
        "name": "Golem Alt",
        "prompt": "Cinematic pixel-art fantasy boss splash art, 16:9, dark muted palette: a massive stone golem with glowing rune cracks, ancient ruins background, no text",
    },
    {
        "id": "boss_assassin_lord_alt",
        "name": "Assassin Lord Alt",
        "prompt": "Cinematic pixel-art fantasy boss splash art, 16:9, dark muted palette: a masked assassin lord with twin curved daggers, crimson cloak, moonlit rooftop, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for boss in BOSSES:
        path = OUT_DIR / f"{boss['id']}.webp"
        if path.exists():
            print(f"Skipping {boss['id']} (exists)")
            continue

        print(f"\nGenerating boss splash: {boss['name']}")
        try:
            img = generate_image(boss["prompt"], api_key)
            fitted = fit_16_9(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {boss['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
