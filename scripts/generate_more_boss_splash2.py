#!/usr/bin/env python3
"""
generate_more_boss_splash2.py
Batch-generate additional boss splash art for Swordjin.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/boss_splash/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "boss_splash"
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


BOSSES = [
    {
        "id": "boss_crimson_matriarch",
        "name": "Crimson Matriarch",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a regal vampire-like queen in torn crimson robes on a throne of weeping statues, blood magic swirling, painterly digital art, no text",
    },
    {
        "id": "boss_ashmont_abomination",
        "name": "Ashmont Abomination",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a towering creature of fused citizens and architecture from a destroyed city, crimson tears raining, painterly digital art, no text",
    },
    {
        "id": "boss_mirror_queen",
        "name": "Mirror Queen",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: an elegant queen made entirely of mirror shards reflecting distorted heroes, infinite hall background, painterly digital art, no text",
    },
    {
        "id": "boss_stormcaller_shaman",
        "name": "Stormcaller Shaman",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a wild shaman with bone fetishes raising lightning above a mountain altar, painterly digital art, no text",
    },
    {
        "id": "boss_lich_of_legion",
        "name": "Lich of the Legion",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: an undead general in tarnished armor commanding a spectral army, blue soul flames, painterly digital art, no text",
    },
    {
        "id": "boss_grief_colossus",
        "name": "Grief Colossus",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a colossal humanoid of stone and moss kneeling in sorrow, waterfalls of tears, painterly digital art, no text",
    },
    {
        "id": "boss_flesh_weaver",
        "name": "Flesh Weaver",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a grotesque surgeon-like creature stitching together monsters in a flesh laboratory, painterly digital art, no text",
    },
    {
        "id": "boss_siren_matriarch",
        "name": "Siren Matriarch",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a beautiful but terrifying sea queen singing on a throne of shipwrecks under a blood moon, painterly digital art, no text",
    },
    {
        "id": "boss_gnarlroot_heart",
        "name": "Gnarlroot Heart",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a pulsing heart of a corrupted forest made of roots and amber sap, surrounded by thorns, painterly digital art, no text",
    },
    {
        "id": "boss_void_herald",
        "name": "Void Herald",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a tall horned entity in star-covered robes opening a rift in reality, tentacles and eyes emerging, painterly digital art, no text",
    },
    {
        "id": "boss_ashmont_king",
        "name": "The Ashmont King",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a fallen king in melted crown and armor wreathed in black fire, ruined throne room, painterly digital art, no text",
    },
    {
        "id": "boss_memory_devourer",
        "name": "Memory Devourer",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a translucent creature feeding on glowing memory shards inside a crystalline vault, painterly digital art, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for boss in BOSSES:
        path = OUT_DIR / f"{boss['id']}.webp"
        if path.exists():
            print(f"Skipping {boss['id']} (exists)")
            continue

        print(f"\nGenerating boss splash: {boss['name']}")
        try:
            img = generate_image(boss["prompt"], api_key)
            fitted = resize_with_letterbox(img, RESOLUTION)
            fitted.save(path, "WEBP", quality=85, method=6)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  ERROR {boss['id']}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
