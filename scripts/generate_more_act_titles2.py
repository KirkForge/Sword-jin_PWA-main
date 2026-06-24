#!/usr/bin/env python3
"""
generate_more_act_titles2.py
Batch-generate additional act/chapter title cards for Swordjin.
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
        "id": "act_prologue_shadows",
        "name": "Prologue: Shadows",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a lone figure standing at the edge of a forest at dusk, first hints of danger, painterly style, no text",
    },
    {
        "id": "act_marked_by_fate",
        "name": "Marked by Fate",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a glowing brand appearing on a warrior's arm under moonlight, painterly style, no text",
    },
    {
        "id": "act_the_crimson_road",
        "name": "The Crimson Road",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a road stained red leading through a valley of fallen banners, painterly style, no text",
    },
    {
        "id": "act_drowned_oaths",
        "name": "Drowned Oaths",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: knights sinking into dark water while clutching broken swords, painterly style, no text",
    },
    {
        "id": "act_ash_and_ivy",
        "name": "Ash and Ivy",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: green vines overtaking burned ruins with small white flowers, painterly style, no text",
    },
    {
        "id": "act_the_siege",
        "name": "The Siege",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: catapults firing against a fortified city under a blood-red dawn, painterly style, no text",
    },
    {
        "id": "act_ghosts_of_legion",
        "name": "Ghosts of the Legion",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: spectral soldiers marching in perfect formation through fog, painterly style, no text",
    },
    {
        "id": "act_the_witchs_bargain",
        "name": "The Witch's Bargain",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a hooded figure signing a contract by candlelight with a clawed hand, painterly style, no text",
    },
    {
        "id": "act_beneath_ashmont",
        "name": "Beneath Ashmont",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a hidden city beneath a ruined capital, bioluminescent fungi and waterfalls, painterly style, no text",
    },
    {
        "id": "act_the_sirens_price",
        "name": "The Siren's Price",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a beautiful ghostly figure singing on a rocky shore with shipwrecks, painterly style, no text",
    },
    {
        "id": "act_fall_of_the_tear",
        "name": "Fall of the Tear",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: a massive crimson wound in the sky closing as the world breaks apart, painterly style, no text",
    },
    {
        "id": "act_epilogue_campfire",
        "name": "Epilogue: Campfire",
        "prompt": "Cinematic 16:9 dark fantasy chapter title card: survivors sitting around a campfire under a clear starry sky, quiet hope, painterly style, no text",
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
