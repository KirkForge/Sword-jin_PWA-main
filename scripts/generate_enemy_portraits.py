#!/usr/bin/env python3
"""
generate_enemy_portraits.py
Batch-generate bestiary portrait art for all enemy types in Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/enemy_portraits/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "enemy_portraits"
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


def fit_to_resolution(img: Image.Image) -> Image.Image:
    img.thumbnail(RESOLUTION, Image.LANCZOS)
    bg = Image.new("RGB", RESOLUTION, (10, 10, 15))
    x = (RESOLUTION[0] - img.width) // 2
    y = (RESOLUTION[1] - img.height) // 2
    bg.paste(img, (x, y))
    return bg


ENEMIES = [
    {
        "type": "skeleton",
        "name": "Skeleton",
        "prompt": "Dark fantasy bestiary portrait: a shambling skeleton warrior with rusted sword and broken shield, hollow eye sockets glowing faint blue, decrepit armor, misty graveyard background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "skeleton_archer",
        "name": "Skeleton Archer",
        "prompt": "Dark fantasy bestiary portrait: a skeleton archer drawing a bone bow, tattered leather quiver, hollow skull with cracked jaw, dim crypt background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "skeleton_captain",
        "name": "Skeleton Captain",
        "prompt": "Dark fantasy bestiary portrait: an armored skeleton captain holding a heraldic shield and notched longsword, broken crown on skull, regal tattered cape, ruined throne hall background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "ghost",
        "name": "Ghost",
        "prompt": "Dark fantasy bestiary portrait: a translucent wailing ghost with clawed hands reaching forward, pale blue spectral light, flickering edges, haunted corridor background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "bandit",
        "name": "Bandit",
        "prompt": "Dark fantasy bestiary portrait: a grinning bandit in rough leather armor, hood pulled low, clutching a serrated dagger, forest road ambush background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "assassin",
        "name": "Assassin",
        "prompt": "Dark fantasy bestiary portrait: a Crimson Fang assassin in crimson cloak and bone fang mask, twin poisoned daggers, crouched predatory stance, shadowed alley background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "golem",
        "name": "Golem",
        "prompt": "Dark fantasy bestiary portrait: a massive stone golem with moss and cracks, glowing runes in its chest, holding an iron halberd, fortress gate background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "necromancer",
        "name": "Necromancer",
        "prompt": "Dark fantasy bestiary portrait: a robed necromancer with a skull staff, hood shadowing emaciated face, green soul-fire in palms, skeletal minions kneeling behind, ritual circle background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "berserker",
        "name": "Berserker",
        "prompt": "Dark fantasy bestiary portrait: a muscular berserker dual-wielding axes, bare chest scarred, eyes bloodshot with battle rage, crimson fang war paint, burning battlefield background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "shaman",
        "name": "Shaman",
        "prompt": "Dark fantasy bestiary portrait: a shaman with a carved wooden mask, feather totems, holding a gnarled staff with elemental gems, aura of orange spirit light, tribal camp background, painterly digital art, centered character, 16:9, no text",
    },
    {
        "type": "wraith",
        "name": "Wraith",
        "prompt": "Dark fantasy bestiary portrait: an elite wraith with tattered royal robes and a crown of black iron, soul drain energy swirling around clawed hands, void realm background, painterly digital art, centered character, 16:9, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for enemy in ENEMIES:
        path = OUT_DIR / f"{enemy['type']}_portrait.webp"
        if path.exists():
            print(f"Skipping {enemy['type']} (exists)")
            continue

        print(f"\nGenerating portrait: {enemy['name']}")
        try:
            img = generate_image(enemy["prompt"], api_key)
            bg = fit_to_resolution(img)
            bg.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {enemy['type']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
