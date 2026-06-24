#!/usr/bin/env python3
"""
generate_more_status.py
Batch-generate additional status effect/buff/debuff icon art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/status/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "status"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (64, 64)


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


def fit_square(img: Image.Image, size: int = 64) -> Image.Image:
    img.thumbnail((size, size), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (15, 15, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


STATUSES = [
    {
        "id": "status_inspired",
        "name": "Inspired",
        "prompt": "Tiny pixel-art RPG status effect icon: a small golden winged quill radiating light, buff, simple, centered, no text",
    },
    {
        "id": "status_marked",
        "name": "Marked",
        "prompt": "Tiny pixel-art RPG status effect icon: a red target reticle with crosshairs on a dark dot, debuff, simple, centered, no text",
    },
    {
        "id": "status_enraged",
        "name": "Enraged",
        "prompt": "Tiny pixel-art RPG status effect icon: a spiked red mask or horned helm with flame aura, berserk buff, simple, centered, no text",
    },
    {
        "id": "status_chilled",
        "name": "Chilled",
        "prompt": "Tiny pixel-art RPG status effect icon: a blue icicle with snow dust, slow debuff, simple, centered, no text",
    },
    {
        "id": "status_electrified",
        "name": "Electrified",
        "prompt": "Tiny pixel-art RPG status effect icon: a small yellow lightning bolt wrapped around a fist, shock debuff, simple, centered, no text",
    },
    {
        "id": "status_corrupted",
        "name": "Corrupted",
        "prompt": "Tiny pixel-art RPG status effect icon: a purple blackened heart dripping dark mist, curse debuff, simple, centered, no text",
    },
    {
        "id": "status_reflected",
        "name": "Reflected",
        "prompt": "Tiny pixel-art RPG status effect icon: a silver mirror shard with a faint arrow bouncing off, reflect buff, simple, centered, no text",
    },
    {
        "id": "status_stealthed",
        "name": "Stealthed",
        "prompt": "Tiny pixel-art RPG status effect icon: a hooded figure dissolving into grey smoke, stealth buff, simple, centered, no text",
    },
    {
        "id": "status_vulnerable",
        "name": "Vulnerable",
        "prompt": "Tiny pixel-art RPG status effect icon: a cracked shield with a red downward arrow, defense debuff, simple, centered, no text",
    },
    {
        "id": "status_invigorated",
        "name": "Invigorated",
        "prompt": "Tiny pixel-art RPG status effect icon: a flexing green arm with glowing energy veins, strength buff, simple, centered, no text",
    },
    {
        "id": "status_doom",
        "name": "Doom",
        "prompt": "Tiny pixel-art RPG status effect icon: a black hourglass with red sand and skull silhouette, countdown debuff, simple, centered, no text",
    },
    {
        "id": "status_blessed",
        "name": "Blessed",
        "prompt": "Tiny pixel-art RPG status effect icon: a small golden halo with sparkling motes, holy buff, simple, centered, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for status in STATUSES:
        path = OUT_DIR / f"{status['id']}.webp"
        if path.exists():
            print(f"Skipping {status['id']} (exists)")
            continue

        print(f"\nGenerating status: {status['name']}")
        try:
            img = generate_image(status["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {status['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
