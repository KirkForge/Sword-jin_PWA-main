#!/usr/bin/env python3
"""
generate_more_npc_variants2.py
Batch-generate additional NPC dialogue portraits for Swordjin (second wave of variants).
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
        "id": "npc_alchemist",
        "name": "Alchemist",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a wild-haired alchemist holding a bubbling flask, stained apron, excited manic grin",
    },
    {
        "id": "npc_gravekeeper",
        "name": "Gravekeeper",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a grim gravekeeper with a shovel, hooded lantern, tired kind eyes",
    },
    {
        "id": "npc_scout",
        "name": "Pathfinder Scout",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a lean scout with a hood and spyglass, dirt on cheeks, cautious alert expression",
    },
    {
        "id": "npc_deserter",
        "name": "Deserter Soldier",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a guilt-ridden deserter in a torn uniform, haunted eyes, unshaven face",
    },
    {
        "id": "npc_knight_errant",
        "name": "Knight Errant",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a young knight errant with a dented helm under arm, idealistic determined look",
    },
    {
        "id": "npc_mystic",
        "name": "Wandering Mystic",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a tattooed mystic with blind white eyes and beaded hair, serene knowing smile",
    },
    {
        "id": "npc_cook",
        "name": "Camp Cook",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a burly camp cook with a wooden spoon, flour dusted beard, jovial expression",
    },
    {
        "id": "npc_librarian",
        "name": "Catacomb Librarian",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a pale librarian with tiny spectacles and ink-stained fingers, fussy nervous expression",
    },
    {
        "id": "npc_ferryman",
        "name": "Styx Ferryman",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a gaunt ferryman with a wide straw hat and pole, inscrutable shadowed face",
    },
    {
        "id": "npc_troubadour",
        "name": "Troubadour",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a flamboyant troubadour with a lute and feathered cap, winking playful expression",
    },
    {
        "id": "npc_informer",
        "name": "Underground Informer",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a ratty informer with a collar popped high, shifty eyes and a crooked knowing smirk",
    },
    {
        "id": "npc_refugee",
        "name": "War Refugee",
        "prompt": "Pixel-art style fantasy RPG NPC portrait, bust shot, 1:1, dark background: a weary refugee wrapped in a patched cloak, clutching a small bundle, hopeful sad eyes",
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
