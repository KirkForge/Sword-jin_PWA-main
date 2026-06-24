#!/usr/bin/env python3
"""
generate_more_skills2.py
Batch-generate additional player skill/ability icons for Swordjin.
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
        "id": "skill_reaping_blade",
        "name": "Reaping Blade",
        "prompt": "Pixel-art style RPG skill icon on dark background: a scythe-like sword sweeping in a wide arc with dark red energy, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_shield_bash",
        "name": "Shield Bash",
        "prompt": "Pixel-art style RPG skill icon on dark background: a tower shield slamming forward with a yellow impact shockwave, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_molten_strike",
        "name": "Molten Strike",
        "prompt": "Pixel-art style RPG skill icon on dark background: a weapon wreathed in orange magma striking the ground, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_frost_armor",
        "name": "Frost Armor",
        "prompt": "Pixel-art style RPG skill icon on dark background: a breastplate covered in jagged ice crystals with blue aura, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_thorn_whip",
        "name": "Thorn Whip",
        "prompt": "Pixel-art style RPG skill icon on dark background: a lash of barbed vines snapping through the air with green thorns, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_smoke_bomb",
        "name": "Smoke Bomb",
        "prompt": "Pixel-art style RPG skill icon on dark background: a small black bomb bursting into grey smoke with a ninja silhouette, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_dominating_shout",
        "name": "Dominating Shout",
        "prompt": "Pixel-art style RPG skill icon on dark background: an open mouth emitting red-orange sound waves and broken chains, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_soul_link",
        "name": "Soul Link",
        "prompt": "Pixel-art style RPG skill icon on dark background: two hearts connected by a silver thread of light, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_grace_of_ash",
        "name": "Grace of Ash",
        "prompt": "Pixel-art style RPG skill icon on dark background: grey ash swirling around a kneeling figure with soft golden light, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_haunting_melody",
        "name": "Haunting Melody",
        "prompt": "Pixel-art style RPG skill icon on dark background: a lute emitting ghostly blue music notes that form skulls, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_timeweaver",
        "name": "Timeweaver",
        "prompt": "Pixel-art style RPG skill icon on dark background: a pocket watch with a cracked glass and spiraling golden threads, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_crimson_pledge",
        "name": "Crimson Pledge",
        "prompt": "Pixel-art style RPG skill icon on dark background: a hand cutting a palm with a dagger over a blood-red banner, centered, ability icon, 1:1, no text",
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
