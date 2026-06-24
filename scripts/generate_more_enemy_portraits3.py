#!/usr/bin/env python3
"""
generate_more_enemy_portraits3.py
Batch-generate additional enemy/boss portrait art for Swordjin (fourth wave).
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/enemy_portraits/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "enemy_portraits"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (256, 256)


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


def fit_square(img: Image.Image, size: int = 256) -> Image.Image:
    img.thumbnail((size, size), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (12, 12, 14))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


ENEMIES = [
    {
        "id": "enemy_blighted_scribe",
        "name": "Blighted Scribe",
        "prompt": "Dark fantasy portrait icon of a rotting scholar with ink-stained fingers and quills stabbed through its neck, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_carrion_beetle",
        "name": "Carrion Beetle",
        "prompt": "Dark fantasy portrait icon of a massive beetle whose shell is made of skulls and bone plates, dripping ichor, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_chained_martyr",
        "name": "Chained Martyr",
        "prompt": "Dark fantasy portrait icon of a tormented holy warrior wrapped in heavy chains with eyes glowing white, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_crimson_acolyte",
        "name": "Crimson Acolyte",
        "prompt": "Dark fantasy portrait icon of a robed cultist with blood running from the eyeholes of a crimson mask, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_drowned_herald",
        "name": "Drowned Herald",
        "prompt": "Dark fantasy portrait icon of a bloated drowned messenger clutching a rusted bell, seaweed hanging from jaw, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_fell_archer",
        "name": "Fell Archer",
        "prompt": "Dark fantasy portrait icon of a skeletal archer drawing a bow of blackened bone with a barbed arrow, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_gnarlroot_seedling",
        "name": "Gnarlroot Seedling",
        "prompt": "Dark fantasy portrait icon of a small walking root creature with glowing green eyes and thorn teeth, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_hollow_myrmidon",
        "name": "Hollow Myrmidon",
        "prompt": "Dark fantasy portrait icon of an empty suit of armor animated by black mist, visor glowing red, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_lich_apprentice",
        "name": "Lich Apprentice",
        "prompt": "Dark fantasy portrait icon of a gaunt necromancer-in-training with a glowing spellbook and missing jaw, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_molten_aberration",
        "name": "Molten Aberration",
        "prompt": "Dark fantasy portrait icon of a humanoid blob of molten slag with fiery cracks and coal eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_rime_witch",
        "name": "Rime Witch",
        "prompt": "Dark fantasy portrait icon of a frostbitten witch with icicle hair and frostbitten blue skin, cruel smile, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_tomb_burrower",
        "name": "Tomb Burrower",
        "prompt": "Dark fantasy portrait icon of a pale eyeless worm erupting from a broken coffin with grave dirt on its segments, circular bust portrait, painterly digital art, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for enemy in ENEMIES:
        path = OUT_DIR / f"{enemy['id']}.webp"
        if path.exists():
            print(f"Skipping {enemy['id']} (exists)")
            continue

        print(f"\nGenerating enemy portrait: {enemy['name']}")
        try:
            img = generate_image(enemy["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {enemy['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
