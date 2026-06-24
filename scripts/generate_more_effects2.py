#!/usr/bin/env python3
"""
generate_more_effects2.py
Batch-generate additional combat effect/spell visual icons for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/effects/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "effects"
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
    bg = Image.new("RGB", (size, size), (18, 18, 22))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


EFFECTS = [
    {
        "id": "fx_molten_eruption",
        "name": "Molten Eruption",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: lava bursting from cracks in the ground with orange-black smoke, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_frost_bloom",
        "name": "Frost Bloom",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a flower of ice crystals blooming outward with cold mist, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_arcane_orb",
        "name": "Arcane Orb",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a swirling sphere of purple and blue runic energy, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_whirling_blades",
        "name": "Whirling Blades",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: multiple ghostly swords spinning in a circle, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_crimson_lance",
        "name": "Crimson Lance",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a spear of solidified blood shooting forward, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_smoke_bomb",
        "name": "Smoke Bomb",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a bursting grey smoke cloud with a ninja silhouette, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_sunburst",
        "name": "Sunburst",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a radiant golden sun exploding with blinding light rays, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_grasping_dead",
        "name": "Grasping Dead",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: skeletal hands bursting from a grave mound to grab enemies, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_wind_cutter",
        "name": "Wind Cutter",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: sharp crescent blades of compressed air, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_mind_flay",
        "name": "Mind Flay",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: ghostly tentacles reaching into a glowing brain silhouette, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_petrify",
        "name": "Petrify",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: a figure turning to grey stone with cracks spreading, centered, game spell icon, 1:1, no text",
    },
    {
        "id": "fx_soul_fire",
        "name": "Soul Fire",
        "prompt": "Pixel-art style RPG combat effect icon on dark background: pale blue-white flames consuming a screaming skull, centered, game spell icon, 1:1, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for effect in EFFECTS:
        path = OUT_DIR / f"{effect['id']}.webp"
        if path.exists():
            print(f"Skipping {effect['id']} (exists)")
            continue

        print(f"\nGenerating effect: {effect['name']}")
        try:
            img = generate_image(effect["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {effect['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
