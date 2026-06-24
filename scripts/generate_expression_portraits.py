#!/usr/bin/env python3
"""
generate_expression_portraits.py
Batch-generate expression variant portraits for Jin and Lyra for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/npcs/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "npcs"
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
    bg = Image.new("RGB", (size, size), (25, 20, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


PORTRAITS = [
    {
        "id": "jin_neutral",
        "name": "Jin Neutral",
        "prompt": "Pixel-art style fantasy RPG protagonist portrait, bust shot, 1:1, dark background: a young swordsman Jin with dark hair and a plain tunic, neutral calm expression, looking slightly left",
    },
    {
        "id": "jin_angry",
        "name": "Jin Angry",
        "prompt": "Pixel-art style fantasy RPG protagonist portrait, bust shot, 1:1, dark background: a young swordsman Jin with dark hair and a plain tunic, angry determined expression, gritted teeth",
    },
    {
        "id": "jin_wounded",
        "name": "Jin Wounded",
        "prompt": "Pixel-art style fantasy RPG protagonist portrait, bust shot, 1:1, dark background: a young swordsman Jin with dark hair, wounded with a cut on cheek, pained but defiant expression",
    },
    {
        "id": "jin_hopeful",
        "name": "Jin Hopeful",
        "prompt": "Pixel-art style fantasy RPG protagonist portrait, bust shot, 1:1, dark background: a young swordsman Jin with dark hair, soft hopeful smile, sunrise light on face",
    },
    {
        "id": "lyra_neutral",
        "name": "Lyra Neutral",
        "prompt": "Pixel-art style fantasy RPG female warrior portrait, bust shot, 1:1, dark background: a blonde warrior woman Lyra in light armor, neutral confident expression, green eyes",
    },
    {
        "id": "lyra_battle",
        "name": "Lyra Battle",
        "prompt": "Pixel-art style fantasy RPG female warrior portrait, bust shot, 1:1, dark background: a blonde warrior woman Lyra in light armor, fierce battle-ready snarl, blood on sword",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for portrait in PORTRAITS:
        path = OUT_DIR / f"{portrait['id']}.webp"
        if path.exists():
            print(f"Skipping {portrait['id']} (exists)")
            continue

        print(f"\nGenerating portrait: {portrait['name']}")
        try:
            img = generate_image(portrait["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {portrait['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
