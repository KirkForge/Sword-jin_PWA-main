#!/usr/bin/env python3
"""
generate_more_enemy_portraits.py
Batch-generate additional enemy/boss portrait art for Swordjin.
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
        "id": "enemy_plague_witch",
        "name": "Plague Witch",
        "prompt": "Dark fantasy portrait icon of a plague witch, hag-like face wrapped in ragged bandages, green vapors, glowing yellow eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_bone_sovereign",
        "name": "Bone Sovereign",
        "prompt": "Dark fantasy portrait icon of a skeletal king wearing a rusted crown and tattered royal cloak, blue soul-flame eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_gnarlroot",
        "name": "Gnarlroot",
        "prompt": "Dark fantasy portrait icon of a corrupted treant, bark skin split by glowing red veins, moss and thorns, angry eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_moonlit_assassin",
        "name": "Moonlit Assassin",
        "prompt": "Dark fantasy portrait icon of a masked elven assassin with silver hair and moon-blades, cold blue eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_iron_golem",
        "name": "Iron Golem",
        "prompt": "Dark fantasy portrait icon of a massive iron golem with riveted plates and glowing furnace eyes, steam vents, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_siren_of_ash",
        "name": "Siren of Ash",
        "prompt": "Dark fantasy portrait icon of an ash-skinned siren with ember hair and mournful glowing eyes, smoke trailing from mouth, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_void_cultist",
        "name": "Void Cultist",
        "prompt": "Dark fantasy portrait icon of a hooded void cultist whose face is a swirling purple-black void, tentacles at hood edges, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_ravager_beast",
        "name": "Ravager Beast",
        "prompt": "Dark fantasy portrait icon of a hulking four-armed beast with cracked hide and dripping jaws, orange bestial eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_grave_warden",
        "name": "Grave Warden",
        "prompt": "Dark fantasy portrait icon of a grave warden knight with a candlelit lantern helm and chainmail, solemn hollow visor, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_frost_revenant",
        "name": "Frost Revenant",
        "prompt": "Dark fantasy portrait icon of a frost revenant, spectral ice armor and frozen beard, pale blue soul eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_blood_mage",
        "name": "Blood Mage",
        "prompt": "Dark fantasy portrait icon of a blood mage with crimson runes painted on pale skin, floating blood droplets, sinister smile, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_the_hollow_prince",
        "name": "The Hollow Prince",
        "prompt": "Dark fantasy portrait icon of the Hollow Prince, a beautiful but empty noble face with cracked porcelain skin and dark tears, circular bust portrait, painterly digital art, no text",
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
