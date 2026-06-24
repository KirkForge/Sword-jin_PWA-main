#!/usr/bin/env python3
"""
generate_more_act_titles.py
Batch-generate additional act/chapter title card art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/act_titles/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "act_titles"
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


def resize_with_letterbox(img: Image.Image, target: tuple) -> Image.Image:
    target_w, target_h = target
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        new_w = target_w
        new_h = int(target_w / img_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * img_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    bg = Image.new("RGB", (target_w, target_h), (8, 8, 10))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


ACT_TITLES = [
    {
        "id": "act_rise_of_the_exile",
        "name": "Rise of the Exile",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: a lone exiled warrior walking a desolate road toward distant burning mountains, dramatic painterly style, no text",
    },
    {
        "id": "act_gardens_of_lament",
        "name": "Gardens of Lament",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: overgrown royal gardens with weeping statues and ghostly white flowers under a full moon, dramatic painterly style, no text",
    },
    {
        "id": "act_the_ashmont_pact",
        "name": "The Ashmont Pact",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: three banners uniting beneath a stormy sky over a war camp, dramatic painterly style, no text",
    },
    {
        "id": "act_drowned_hopes",
        "name": "Drowned Hopes",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: a flooded cathedral interior with light shafts piercing murky green water, dramatic painterly style, no text",
    },
    {
        "id": "act_chains_of_the_past",
        "name": "Chains of the Past",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: spectral chains rising from a battlefield graveyard toward a blood-red eclipse, dramatic painterly style, no text",
    },
    {
        "id": "act_war_for_the_crimson_tear",
        "name": "War for the Crimson Tear",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: two armies clashing beneath a sky torn by a bleeding red rift, dramatic painterly style, no text",
    },
    {
        "id": "act_throne_of_echoes",
        "name": "Throne of Echoes",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: an empty obsidian throne in a vast hall lined with whispering statues, dramatic painterly style, no text",
    },
    {
        "id": "act_the_last_refusal",
        "name": "The Last Refusal",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: a warrior standing at the edge of a luminous void, letting go of a cursed sword, peaceful defiance, dramatic painterly style, no text",
    },
    {
        "id": "act_vengeance_road",
        "name": "Vengeance Road",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: a hooded figure on a horse riding through a burning village at dusk, dramatic painterly style, no text",
    },
    {
        "id": "act_hollow_alliance",
        "name": "Hollow Alliance",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: uneasy allies from rival factions standing back-to-back in a torchlit ruin, dramatic painterly style, no text",
    },
    {
        "id": "act_memory_vault",
        "name": "Memory Vault",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: a crystalline vault floating with shards showing scenes of past battles, purple void background, dramatic painterly style, no text",
    },
    {
        "id": "act_beyond_the_tear",
        "name": "Beyond the Tear",
        "prompt": "Cinematic dark fantasy RPG chapter title card 16:9: a gateway of crimson light opening onto an alien starfield, dramatic painterly style, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for act in ACT_TITLES:
        path = OUT_DIR / f"{act['id']}.webp"
        if path.exists():
            print(f"Skipping {act['id']} (exists)")
            continue

        print(f"\nGenerating act title: {act['name']}")
        try:
            img = generate_image(act["prompt"], api_key)
            fitted = resize_with_letterbox(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {act['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
