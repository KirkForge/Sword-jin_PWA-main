#!/usr/bin/env python3
"""
generate_more_npc_variants.py
Batch-generate additional NPC dialogue portraits for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/npcs/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "npcs"
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
    bg = Image.new("RGB", (size, size), (25, 20, 18))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    bg.paste(img, (x, y))
    return bg


NPCS = [
    {
        "id": "npc_merchant",
        "name": "Traveling Merchant",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a grinning merchant with a wide-brimmed hat, jingling coin purse, and knowing eyes",
    },
    {
        "id": "npc_innkeeper",
        "name": "Innkeeper",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a stout innkeeper with a towel over shoulder, tankard in hand, warm welcoming smile",
    },
    {
        "id": "npc_herbalist",
        "name": "Herbalist",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: an elderly herbalist with wildflower crown, dried herbs hanging, gentle focused expression",
    },
    {
        "id": "npc_hunter",
        "name": "Hunter",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a grizzled hunter with fur-lined cloak, bow in hand, and alert expression",
    },
    {
        "id": "npc_oracle",
        "name": "Blind Oracle",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a blindfolded oracle with glowing eye markings, flowing robes, serene mysterious expression",
    },
    {
        "id": "npc_smuggler",
        "name": "Smuggler",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a wiry smuggler with bandana, hidden knives, and a sly untrusting smirk",
    },
    {
        "id": "npc_paladin",
        "name": "Paladin Captain",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a stern paladin with gleaming armor, holy sun emblem, intense righteous gaze",
    },
    {
        "id": "npc_witch",
        "name": "Coven Witch",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a pale witch with raven hair, bone jewelry, and a calculating half-smile",
    },
    {
        "id": "npc_bard",
        "name": "Wandering Bard",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a charming bard with feathered cap, lute peeking over back, playful grin",
    },
    {
        "id": "npc_prisoner",
        "name": "Freed Prisoner",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a gaunt prisoner with broken shackles, fearful but grateful eyes, ragged clothes",
    },
    {
        "id": "npc_golem",
        "name": "Awakened Golem",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a craggy stone golem with glowing rune eyes, cracks showing warm light, stoic expression",
    },
    {
        "id": "npc_child",
        "name": "Street Urchin",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a dirty-faced street child with oversized stolen coat, hopeful wide eyes",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for npc in NPCS:
        path = OUT_DIR / f"{npc['id']}.webp"
        if path.exists():
            print(f"Skipping {npc['id']} (exists)")
            continue

        print(f"\nGenerating NPC portrait: {npc['name']}")
        try:
            img = generate_image(npc["prompt"], api_key)
            square = fit_square(img, RESOLUTION[0])
            square.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {npc['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
