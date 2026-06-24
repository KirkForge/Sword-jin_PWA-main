#!/usr/bin/env python3
"""
generate_act_title_cards.py
Batch-generate act transition title card art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/act_titles/
"""

import base64
import os
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
    bg = Image.new("RGB", (target_w, target_h), (10, 10, 12))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    bg.paste(img, (x, y))
    return bg


def overlay_title(img: Image.Image, text: str) -> Image.Image:
    # Return a title-only copy and a raw copy? Just return raw for now; title added by Godot UI.
    return img


ACTS = [
    {
        "id": "act01",
        "name": "Act I — The Broken Sword",
        "prompt": "Cinematic dark fantasy title card art 16:9: a lone warrior's silhouette holding a broken sword against a stormy dawn sky, ruined battlefield, somber and determined mood, painterly digital art, epic composition, no text",
    },
    {
        "id": "act02",
        "name": "Act II — The Iron Road",
        "prompt": "Cinematic dark fantasy title card art 16:9: a winding ancient road through misty hills leading to a distant iron gate, lanterns glowing in fog, mysterious journey mood, painterly digital art, epic composition, no text",
    },
    {
        "id": "act03",
        "name": "Act III — Betrayal",
        "prompt": "Cinematic dark fantasy title card art 16:9: a crimson fang cultist standing in shadowed ruins, blood-red moon overhead, treachery and dread mood, painterly digital art, epic composition, no text",
    },
    {
        "id": "act04",
        "name": "Act IV — Alliance",
        "prompt": "Cinematic dark fantasy title card art 16:9: three war banners of different houses raised together on a hilltop at sunrise, army camp below, hope and alliance mood, painterly digital art, epic composition, no text",
    },
    {
        "id": "act05",
        "name": "Act V — War",
        "prompt": "Cinematic dark fantasy title card art 16:9: a massive siege battle before a dark tower, catapults firing, banners and smoke, epic war mood, painterly digital art, no text",
    },
    {
        "id": "act06",
        "name": "Act VI — Descent",
        "prompt": "Cinematic dark fantasy title card art 16:9: a lone swordsman descending into a swirling purple void of stars and ghostly memories, surreal and solemn mood, painterly digital art, epic composition, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for act in ACTS:
        path = OUT_DIR / f"{act['id']}_title.webp"
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
