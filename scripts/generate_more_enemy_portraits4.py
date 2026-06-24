#!/usr/bin/env python3
"""
generate_more_enemy_portraits4.py
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
    {"id": "enemy_bone_corsair", "name": "Bone Corsair", "prompt": "Dark fantasy portrait icon of a skeletal pirate with a tricorn hat and rusted cutlass, sea mist, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_cabal_summoner", "name": "Cabal Summoner", "prompt": "Dark fantasy portrait icon of a hooded figure with a tentacle emerging from their sleeve and a glowing summoning circle, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_cinder_wretch", "name": "Cinder Wretch", "prompt": "Dark fantasy portrait icon of a burned humanoid with embers glowing in cracked charcoal skin, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_crypt_knight", "name": "Crypt Knight", "prompt": "Dark fantasy portrait icon of an armored knight in moldy tabard holding a notched burial sword, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_fang_thrall", "name": "Fang Thrall", "prompt": "Dark fantasy portrait icon of a feral human with elongated canines and clawed hands, blood on mouth, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_harrowed_mage", "name": "Harrowed Mage", "prompt": "Dark fantasy portrait icon of a mage whose face is half-turned to spell-burned crystal, one eye glowing, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_mire_stalker", "name": "Mire Stalker", "prompt": "Dark fantasy portrait icon of a lean predator camouflaged in swamp reeds with glowing yellow eyes, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_penitent_giant", "name": "Penitent Giant", "prompt": "Dark fantasy portrait icon of a giant wrapped in prayer chains and iron crosses, sorrowful eyes, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_ash_serpent", "name": "Ash Serpent", "prompt": "Dark fantasy portrait icon of a snake made of compacted ash and cinders with glowing coal eyes, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_soul_merchant", "name": "Soul Merchant", "prompt": "Dark fantasy portrait icon of a gaunt merchant in rich robes weighing souls on a handheld scale, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_thrall_of_tear", "name": "Thrall of the Tear", "prompt": "Dark fantasy portrait icon of a corrupted soldier with a crimson tear glowing in their chest and empty eyes, circular bust portrait, painterly digital art, no text"},
    {"id": "enemy_void_scribe", "name": "Void Scribe", "prompt": "Dark fantasy portrait icon of a scribe whose hands are ink-black tentacles writing on floating parchment, circular bust portrait, painterly digital art, no text"},
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
