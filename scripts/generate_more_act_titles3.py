#!/usr/bin/env python3
"""
generate_more_act_titles3.py
Batch-generate additional act/chapter title cards for Swordjin (third wave).
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
        "id": "act_whispers_of_legion",
        "name": "Whispers of the Legion",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: spectral soldiers whispering from the walls of a half-collapsed fortress, painterly style, no text",
    },
    {
        "id": "act_the_hollow_crown",
        "name": "The Hollow Crown",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a broken royal crown on a stone pedestal surrounded by kneeling shadows, painterly style, no text",
    },
    {
        "id": "act_oath_of_ash",
        "name": "Oath of Ash",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a warrior kneeling among ashes while grey embers swirl into the shape of a sword, painterly style, no text",
    },
    {
        "id": "act_march_of_the_crimson_tear",
        "name": "March of the Crimson Tear",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: an army marching beneath a bleeding red rift in the sky, painterly style, no text",
    },
    {
        "id": "act_siren_song",
        "name": "Siren Song",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a ghostly figure singing on a cliff while ships break on rocks below, painterly style, no text",
    },
    {
        "id": "act_legion_reborn",
        "name": "Legion Reborn",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: spectral banners reigniting with blue flame as dead soldiers rise in ordered ranks, painterly style, no text",
    },
    {
        "id": "act_thorns_of_memory",
        "name": "Thorns of Memory",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a garden of black roses with ghostly faces blooming among the thorns, painterly style, no text",
    },
    {
        "id": "act_the_final_oath",
        "name": "The Final Oath",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: two warriors clasping hands on a battlefield at sunset, bloodied but unbowed, painterly style, no text",
    },
    {
        "id": "act_hollow_alliance",
        "name": "Hollow Alliance",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a living knight and a spectral knight standing back-to-back against encircling shadows, painterly style, no text",
    },
    {
        "id": "act_beneath_the_tear",
        "name": "Beneath the Tear",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: figures descending into a cavernous wound in the earth that glows crimson from within, painterly style, no text",
    },
    {
        "id": "act_memory_vault",
        "name": "Memory Vault",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: an endless hall of floating glass shards each showing a different past battle, painterly style, no text",
    },
    {
        "id": "act_rise_of_ashmont",
        "name": "Rise of Ashmont",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a ruined capital rebuilding itself from smoke and golden light, hope amid devastation, painterly style, no text",
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
