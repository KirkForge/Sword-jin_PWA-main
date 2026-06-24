#!/usr/bin/env python3
"""
generate_more_act_titles5.py
Batch-generate additional act/chapter title cards for Swordjin (sixth wave).
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
    {"id": "act_rust_and_ritual", "name": "Rust and Ritual", "prompt": "Cinematic 16:9 dark fantasy chapter title card: a broken sword embedded in a stone altar surrounded by guttering candles, painterly style, no text"},
    {"id": "act_the_blood_ledger", "name": "The Blood Ledger", "prompt": "Cinematic 16:9 dark fantasy chapter title card: a massive open book with names written in blood and a red quill floating above it, painterly style, no text"},
    {"id": "act_ash_and_resolve", "name": "Ash and Resolve", "prompt": "Cinematic 16:9 dark fantasy chapter title card: a lone figure sharpening a sword in a grey ashen wasteland, painterly style, no text"},
    {"id": "act_hollow_vows", "name": "Hollow Vows", "prompt": "Cinematic 16:9 dark fantasy chapter title card: wedding rings scattered among broken armor in a ruined chapel, painterly style, no text"},
    {"id": "act_covenant_of_fang", "name": "Covenant of Fang", "prompt": "Cinematic 16:9 dark fantasy chapter title card: warriors drinking from a shared chalice while wolves watch from the shadows, painterly style, no text"},
    {"id": "act_the_sunken_oath", "name": "The Sunken Oath", "prompt": "Cinematic 16:9 dark fantasy chapter title card: a drowned banner floating just beneath the surface of black water, painterly style, no text"},
    {"id": "act_scars_of_sunfall", "name": "Scars of Sunfall", "prompt": "Cinematic 16:9 dark fantasy chapter title card: a fortress wall covered in claw marks while the setting sun bleeds red, painterly style, no text"},
    {"id": "act_march_of_hollows", "name": "March of Hollows", "prompt": "Cinematic 16:9 dark fantasy chapter title card: an army of faceless soldiers marching through a burnt forest, painterly style, no text"},
    {"id": "act_the_widow_tithe", "name": "The Widow Tithe", "prompt": "Cinematic 16:9 dark fantasy chapter title card: veiled figures offering silver coins to a robed collector at a crossroads, painterly style, no text"},
    {"id": "act_throne_of_dust", "name": "Throne of Dust", "prompt": "Cinematic 16:9 dark fantasy chapter title card: an empty throne crumbling into sand and bone in a dark hall, painterly style, no text"},
    {"id": "act_bound_by_memory", "name": "Bound by Memory", "prompt": "Cinematic 16:9 dark fantasy chapter title card: glowing chains of memory wrapping around a warrior and a ghost, painterly style, no text"},
    {"id": "act_the_world_remembered", "name": "The World Remembered", "prompt": "Cinematic 16:9 dark fantasy chapter title card: a vast landscape restoring itself from grey ash into green life under golden light, painterly style, no text"},
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
