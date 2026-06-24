#!/usr/bin/env python3
"""
generate_more_enemy_portraits2.py
Batch-generate additional enemy/boss portrait art for Swordjin (third wave).
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
        "id": "enemy_mire_matron",
        "name": "Mire Matron",
        "prompt": "Dark fantasy portrait icon of a bloated swamp matron witch with algae hair and milky eyes, dripping green muck, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_ashen_hound",
        "name": "Ashen Hound",
        "prompt": "Dark fantasy portrait icon of a skeletal hound wreathed in grey ash with glowing ember eyes and bared fangs, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_crimson_herald",
        "name": "Crimson Herald",
        "prompt": "Dark fantasy portrait icon of a gaunt herald in a tattered red tabard holding a war horn, hollow eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_bog_broodmother",
        "name": "Bog Broodmother",
        "prompt": "Dark fantasy portrait icon of a hunched amphibian queen with egg sacs and toothed maw, swamp slime, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_ashborne_knight",
        "name": "Ashborne Knight",
        "prompt": "Dark fantasy portrait icon of a blackened plate-armored knight with smoke seeping from helm joints, red slit visor, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_siren_reaper",
        "name": "Siren Reaper",
        "prompt": "Dark fantasy portrait icon of a drowned siren with seaweed hair and a rusted sickle, pale dead eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_legion_standard",
        "name": "Legion Standard",
        "prompt": "Dark fantasy portrait icon of a spectral legion banner-bearer whose face is a skull beneath a broken helm, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_vermin_king",
        "name": "Vermin King",
        "prompt": "Dark fantasy portrait icon of a hulking rat-man warlord with one blind eye and a crown of bone, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_glass_sorceress",
        "name": "Glass Sorceress",
        "prompt": "Dark fantasy portrait icon of a sorceress with skin like cracked stained glass and prismatic light bleeding through, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_fang_collector",
        "name": "Fang Collector",
        "prompt": "Dark fantasy portrait icon of a grinning mercenary wearing a necklace of teeth and mismatched armor, cruel eyes, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_wandering_pyre",
        "name": "Wandering Pyre",
        "prompt": "Dark fantasy portrait icon of a burning corpse entity with a skull face and arms of flame, circular bust portrait, painterly digital art, no text",
    },
    {
        "id": "enemy_vestige_lord",
        "name": "Vestige Lord",
        "prompt": "Dark fantasy portrait icon of a translucent noble ghost with a cracked crown and sorrowful expression, circular bust portrait, painterly digital art, no text",
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
