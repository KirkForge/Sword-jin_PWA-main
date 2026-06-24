#!/usr/bin/env python3
"""
generate_more_concept.py
Batch-generate additional story/concept key art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/concept/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "concept"
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


CONCEPTS = [
    {
        "id": "story_the_betrayal",
        "name": "The Betrayal",
        "prompt": "Cinematic dark fantasy story scene 16:9: a cloaked figure driving a dagger into the back of a trusting warrior under moonlit ruins, dramatic shadows, painterly digital art, no text",
    },
    {
        "id": "story_alliance_oath",
        "name": "Alliance Oath",
        "prompt": "Cinematic dark fantasy story scene 16:9: three warriors from different banners clasping hands in a torchlit war tent, solemn alliance moment, painterly digital art, no text",
    },
    {
        "id": "story_siege_of_ashmont",
        "name": "Siege of Ashmont",
        "prompt": "Cinematic dark fantasy story scene 16:9: a massive army charging a dark fortress wall under a stormy sky, catapults and banners, painterly digital art, no text",
    },
    {
        "id": "story_tower_ascension",
        "name": "Tower Ascension",
        "prompt": "Cinematic dark fantasy story scene 16:9: a lone swordsman climbing a spiraling dark tower interior with red light from above, painterly digital art, no text",
    },
    {
        "id": "story_memory_shard",
        "name": "Memory Shard",
        "prompt": "Cinematic dark fantasy story scene 16:9: a warrior reaching toward a floating crystalline shard that reflects ghostly memories, purple void background, painterly digital art, no text",
    },
    {
        "id": "story_final_refusal",
        "name": "The Final Refusal",
        "prompt": "Cinematic dark fantasy story scene 16:9: a warrior kneeling and setting down a cursed sword at the edge of a luminous void, peaceful defiance, painterly digital art, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for concept in CONCEPTS:
        path = OUT_DIR / f"{concept['id']}.webp"
        if path.exists():
            print(f"Skipping {concept['id']} (exists)")
            continue

        print(f"\nGenerating concept: {concept['name']}")
        try:
            img = generate_image(concept["prompt"], api_key)
            fitted = resize_with_letterbox(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {concept['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
