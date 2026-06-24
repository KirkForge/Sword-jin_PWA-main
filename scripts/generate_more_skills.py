#!/usr/bin/env python3
"""
generate_more_skills.py
Batch-generate additional combat skill/ability icon art for Swordjin.
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


def fit_square(img: Image.Image, size: int = 128) -> Image.Image:
    img.thumbnail((size, size), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (20, 20, 25))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


SKILLS = [
    {
        "id": "skill_counter_strike",
        "name": "Counter Strike",
        "prompt": "Pixel-art style RPG ability icon on dark background: a sword catching an enemy blade and redirecting with a bright amber spark, defensive counterattack, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_rend",
        "name": "Rend",
        "prompt": "Pixel-art style RPG ability icon on dark background: three cruel claw slashes leaving glowing red wound trails, bleeding damage, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_vanguard_charge",
        "name": "Vanguard Charge",
        "prompt": "Pixel-art style RPG ability icon on dark background: an armored shoulder slam with a blue forward shockwave, charging attack, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_last_stand",
        "name": "Last Stand",
        "prompt": "Pixel-art style RPG ability icon on dark background: a lone warrior holding a cracked shield as golden light rises, desperate defense buff, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_battle_cry",
        "name": "Battle Cry",
        "prompt": "Pixel-art style RPG ability icon on dark background: an open war-horn emitting orange sound waves and confetti-like sparks, party buff, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_arcane_blade",
        "name": "Arcane Blade",
        "prompt": "Pixel-art style RPG ability icon on dark background: a longsword humming with purple runes and magical glyphs, magic weapon buff, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_holy_smite",
        "name": "Holy Smite",
        "prompt": "Pixel-art style RPG ability icon on dark background: a golden hammer falling from a beam of light onto dark ground, radiant damage, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_shadow_step",
        "name": "Shadow Step",
        "prompt": "Pixel-art style RPG ability icon on dark background: a figure dissolving into black smoke and reappearing as a silhouette, teleport strike, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_trap_spring",
        "name": "Trap Spring",
        "prompt": "Pixel-art style RPG ability icon on dark background: a metal bear trap snapping shut with yellow sparks, crowd control, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_piercing_shot",
        "name": "Piercing Shot",
        "prompt": "Pixel-art style RPG ability icon on dark background: an arrow with a spiraling white trail piercing through multiple targets, ranged penetration, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_life_drain",
        "name": "Life Drain",
        "prompt": "Pixel-art style RPG ability icon on dark background: a red tendril connecting a skull to a heart, siphoning life essence, centered, game skill icon, 1:1, no text",
    },
    {
        "id": "skill_divine_protection",
        "name": "Divine Protection",
        "prompt": "Pixel-art style RPG ability icon on dark background: a golden dome shield with winged edges and soft glowing particles, powerful defensive buff, centered, game skill icon, 1:1, no text",
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

        print(f"\nGenerating skill: {skill['name']}")
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
