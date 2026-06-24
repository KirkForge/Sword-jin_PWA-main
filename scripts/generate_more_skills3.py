#!/usr/bin/env python3
"""
generate_more_skills3.py
Batch-generate additional player skill/ability icons for Swordjin (third wave).
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
        "id": "skill_blood_rite",
        "name": "Blood Rite",
        "prompt": "Pixel-art style RPG skill icon on dark background: a hand drawing a crimson ritual circle that glows with runes, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_spectral_armor",
        "name": "Spectral Armor",
        "prompt": "Pixel-art style RPG skill icon on dark background: translucent ghostly plate armor with blue soul-flame accents, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_venom_strike",
        "name": "Venom Strike",
        "prompt": "Pixel-art style RPG skill icon on dark background: a dripping green dagger striking a target with poison splatter, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_chain_pull",
        "name": "Chain Pull",
        "prompt": "Pixel-art style RPG skill icon on dark background: a hooked chain lashing out and pulling an enemy silhouette, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_sunburst_slash",
        "name": "Sunburst Slash",
        "prompt": "Pixel-art style RPG skill icon on dark background: a sword swing leaving a blazing golden arc and rays, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_void_step",
        "name": "Void Step",
        "prompt": "Pixel-art style RPG skill icon on dark background: a figure stepping through a purple-black tear in reality, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_rallying_cry",
        "name": "Rallying Cry",
        "prompt": "Pixel-art style RPG skill icon on dark background: a war horn emitting golden sound waves and rising banners, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_bone_prison",
        "name": "Bone Prison",
        "prompt": "Pixel-art style RPG skill icon on dark background: skeletal hands rising from the ground to cage a target, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_thunderclap",
        "name": "Thunderclap",
        "prompt": "Pixel-art style RPG skill icon on dark background: a hammer falling from storm clouds with lightning impact, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_life_transfer",
        "name": "Life Transfer",
        "prompt": "Pixel-art style RPG skill icon on dark background: a red stream of life flowing from one heart to another across clasped hands, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_iron_sigil",
        "name": "Iron Sigil",
        "prompt": "Pixel-art style RPG skill icon on dark background: a glowing iron brand/sigil on a shield that pulses with protection, centered, ability icon, 1:1, no text",
    },
    {
        "id": "skill_mirrored_strike",
        "name": "Mirrored Strike",
        "prompt": "Pixel-art style RPG skill icon on dark background: two identical sword swings mirrored around a silver shard, centered, ability icon, 1:1, no text",
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
