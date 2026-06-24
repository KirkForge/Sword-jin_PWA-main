#!/usr/bin/env python3
"""
generate_more_skills4.py
Batch-generate additional player skill/ability icons for Swordjin (fourth wave).
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/skills/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "skills"
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
    bg = Image.new("RGB", (size, size), (22, 22, 26))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


SKILLS = [
    {
        "id": "skill_ash_summons",
        "name": "Ash Summons",
        "prompt": "Pixel-art style RPG skill icon on dark background: a swirling cloud of grey ash forming into a warrior's silhouette, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_blade_dance",
        "name": "Blade Dance",
        "prompt": "Pixel-art style RPG skill icon on dark background: multiple sword slashes forming a spiraling pattern of silver arcs, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_blood_harvest",
        "name": "Blood Harvest",
        "prompt": "Pixel-art style RPG skill icon on dark background: a scythe sweeping red essence into a swirling crimson orb, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_crimson_rush",
        "name": "Crimson Rush",
        "prompt": "Pixel-art style RPG skill icon on dark background: a figure dashing forward leaving a red afterimage trail, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_frozen_grasp",
        "name": "Frozen Grasp",
        "prompt": "Pixel-art style RPG skill icon on dark background: a skeletal hand of blue ice reaching from below to clutch a target, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_hallow_strike",
        "name": "Hallow Strike",
        "prompt": "Pixel-art style RPG skill icon on dark background: a weapon blazing with golden light striking a shadow, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_iron_mantle",
        "name": "Iron Mantle",
        "prompt": "Pixel-art style RPG skill icon on dark background: a cloak of interlocking iron scales wrapping around a silhouette, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_marrow_drain",
        "name": "Marrow Drain",
        "prompt": "Pixel-art style RPG skill icon on dark background: a green ghostly tendril sucking life essence from a cracked bone, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_phantom_dash",
        "name": "Phantom Dash",
        "prompt": "Pixel-art style RPG skill icon on dark background: a translucent figure blinking through a wall of mist, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_soul_shatter",
        "name": "Soul Shatter",
        "prompt": "Pixel-art style RPG skill icon on dark background: a glowing spirit cracked into shards by an impact, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_tear_ward",
        "name": "Tear Ward",
        "prompt": "Pixel-art style RPG skill icon on dark background: a crimson rift sealed by a circle of binding runes, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_wraith_lash",
        "name": "Wraith Lash",
        "prompt": "Pixel-art style RPG skill icon on dark background: a whip of ghostly energy curling around a target, centered, ability icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for skill in SKILLS:
        path = OUT_DIR / f"{skill['id']}.webp"
        if path.exists():
            print(f"Skipping {skill['id']} (exists)")
            continue

        print(f"\nGenerating skill icon: {skill['name']}")
        try:
            img = generate_image(skill["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {skill['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
