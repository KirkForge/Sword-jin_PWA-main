#!/usr/bin/env python3
"""
generate_more_npc_variants3.py
Batch-generate additional NPC dialogue portraits for Swordjin (third wave of variants).
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
    {"id": "npc_apothecary", "name": "Apothecary", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a severe apothecary with mortar and pestle, bandaged hands, intense judging expression"},
    {"id": "npc_bounty_hunter", "name": "Bounty Hunter", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a scarred bounty hunter with a crossbow slung over shoulder and cold calculating eyes"},
    {"id": "npc_chronomancer", "name": "Chronomancer", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: an old chronomancer with hourglass earrings and clockwork eye, absent-minded smile"},
    {"id": "npc_cult_defector", "name": "Cult Defector", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a nervous ex-cultist with burn scars and wide fearful eyes, clutching a hidden knife"},
    {"id": "npc_dockmaster", "name": "Dockmaster", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a weathered dockmaster with tar-stained hands and a pipe, gruff but fair expression"},
    {"id": "npc_exorcist", "name": "Exorcist", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a gaunt exorcist with silver talismans and tired compassionate eyes"},
    {"id": "npc_gardener_royal", "name": "Royal Gardener", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: an elderly gardener in straw hat holding black roses, kind melancholic smile"},
    {"id": "npc_jeweler", "name": "Jeweler", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a meticulous jeweler with loupe and magnifying glass examining a soul gem"},
    {"id": "npc_mapmaker", "name": "Mapmaker", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a half-blind mapmaker with ink-stained fingers and a rolled chart, eager expression"},
    {"id": "npc_mercenary_captain", "name": "Mercenary Captain", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a grizzled mercenary captain with a bronze gorget and contemptuous smirk"},
    {"id": "npc_relic_dealer", "name": "Relic Dealer", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a shifty relic dealer with a coat lined in strange charms and a toothy grin"},
    {"id": "npc_warden", "name": "Warden", "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a stern prison warden with iron-gray hair, keys jingling, suspicious glare"},
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
