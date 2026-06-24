#!/usr/bin/env python3
"""
generate_more_act_titles4.py
Batch-generate additional act/chapter title cards for Swordjin (fifth wave).
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
        "id": "act_fall_of_legion",
        "name": "Fall of the Legion",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: spectral banners falling from a storm-wracked sky as a doomed legion kneels in the mud, painterly style, no text",
    },
    {
        "id": "act_crimson_augury",
        "name": "Crimson Augury",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a fortune teller reading prophecies in a pool of blood that reflects a burning city, painterly style, no text",
    },
    {
        "id": "act_ashen_march",
        "name": "The Ashen March",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: an endless column of soldiers walking through a landscape of grey ash and dead trees, painterly style, no text",
    },
    {
        "id": "act_tear_of_dreams",
        "name": "Tear of Dreams",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a sleeping figure beneath a night sky where the stars form the shape of a weeping eye, painterly style, no text",
    },
    {
        "id": "act_ghost_parade",
        "name": "Ghost Parade",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a procession of translucent spirits walking through a moonlit ruined boulevard, painterly style, no text",
    },
    {
        "id": "act_throne_of_sorrow",
        "name": "Throne of Sorrow",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a lonely figure sitting on a throne made of weeping faces in a vaulted hall, painterly style, no text",
    },
    {
        "id": "act_blackwater_bay",
        "name": "Blackwater Bay",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a foggy pirate bay with ghost galleons and crimson lanterns reflected in black water, painterly style, no text",
    },
    {
        "id": "act_elegy_of_stars",
        "name": "Elegy of Stars",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a bard silhouetted against a sky where constellations are slowly extinguished one by one, painterly style, no text",
    },
    {
        "id": "act_last_bastion",
        "name": "The Last Bastion",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a fortified hilltop abbey surrounded by an ocean of shadowy besiegers, painterly style, no text",
    },
    {
        "id": "act_soul_market",
        "name": "Soul Market",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a bazaar of hooded merchants trading glowing soul orbs beneath twisted archways, painterly style, no text",
    },
    {
        "id": "act_widow_march",
        "name": "Widow's March",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a line of black-veiled figures walking across a battlefield collecting the weapons of the fallen, painterly style, no text",
    },
    {
        "id": "act_iron_requiem",
        "name": "Iron Requiem",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a battlefield cemetery of rusted armor and swords arranged like a graveyard under twilight, painterly style, no text",
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
