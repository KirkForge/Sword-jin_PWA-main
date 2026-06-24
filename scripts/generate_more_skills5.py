#!/usr/bin/env python3
"""
generate_more_skills5.py
Batch-generate additional player skill/ability icons for Swordjin (fifth wave).
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
    {"id": "skill_ancestral_roar", "name": "Ancestral Roar", "prompt": "Pixel-art style RPG skill icon on dark background: a roaring spectral warrior face surrounded by golden sound rings, centered, ability icon, 1:1, no text"},
    {"id": "skill_brand_of_ash", "name": "Brand of Ash", "prompt": "Pixel-art style RPG skill icon on dark background: a burning handprint brand searing into a target, centered, ability icon, 1:1, no text"},
    {"id": "skill_crimson_gift", "name": "Crimson Gift", "prompt": "Pixel-art style RPG skill icon on dark background: one figure offering a glowing red heart to another across a blood link, centered, ability icon, 1:1, no text"},
    {"id": "skill_desperate_lunge", "name": "Desperate Lunge", "prompt": "Pixel-art style RPG skill icon on dark background: a figure launching forward with blade extended leaving a red desperation trail, centered, ability icon, 1:1, no text"},
    {"id": "skill_fates_intervention", "name": "Fate's Intervention", "prompt": "Pixel-art style RPG skill icon on dark background: a pair of ethereal hands rearranging glowing threads of fate, centered, ability icon, 1:1, no text"},
    {"id": "skill_hallowed_ground", "name": "Hallowed Ground", "prompt": "Pixel-art style RPG skill icon on dark background: a circle of consecrated earth with golden light pushing back shadows, centered, ability icon, 1:1, no text"},
    {"id": "skill_maw_of_earth", "name": "Maw of Earth", "prompt": "Pixel-art style RPG skill icon on dark background: a jagged fissure opening in the ground with teeth-like stone spikes, centered, ability icon, 1:1, no text"},
    {"id": "skill_punishing_blow", "name": "Punishing Blow", "prompt": "Pixel-art style RPG skill icon on dark background: a massive overhand strike with a glowing hammer of judgment, centered, ability icon, 1:1, no text"},
    {"id": "skill_silver_nets", "name": "Silver Nets", "prompt": "Pixel-art style RPG skill icon on dark background: a net of silver chain links thrown to capture a shadowy form, centered, ability icon, 1:1, no text"},
    {"id": "skill_soul_syphon", "name": "Soul Syphon", "prompt": "Pixel-art style RPG skill icon on dark background: a ghostly tube draining blue essence from a heart into a flask, centered, ability icon, 1:1, no text"},
    {"id": "skill_vortex_blade", "name": "Vortex Blade", "prompt": "Pixel-art style RPG skill icon on dark background: a sword spinning at the center of a pulling air vortex, centered, ability icon, 1:1, no text"},
    {"id": "skill_withering_touch", "name": "Withering Touch", "prompt": "Pixel-art style RPG skill icon on dark background: a hand leaving a trail of black decay and wilting plants, centered, ability icon, 1:1, no text"},
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
