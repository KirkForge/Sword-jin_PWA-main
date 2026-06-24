#!/usr/bin/env python3
"""
generate_more_boss_splash.py
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


BOSSES = [
    {
        "id": "boss_plague_witch",
        "name": "Plague Witch",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a plague witch hovering in a ruined apothecary, green toxic clouds, glowing eyes, horrifying silhouette, painterly digital art, no text",
    },
    {
        "id": "boss_bone_sovereign",
        "name": "Bone Sovereign",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a skeletal king on a throne of stacked bones wearing a rusted crown, blue soul flames, painterly digital art, no text",
    },
    {
        "id": "boss_gnarlroot",
        "name": "Gnarlroot",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a massive corrupted treant bursting through a forest clearing, red sap veins and thorn whips, painterly digital art, no text",
    },
    {
        "id": "boss_iron_golem",
        "name": "Iron Golem",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a towering iron golem in a collapsed forge, glowing furnace eyes, steam and molten metal, painterly digital art, no text",
    },
    {
        "id": "boss_void_cultist",
        "name": "Void Cultist",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: a hooded void cultist opening a dimensional tear with tentacles pouring out, purple-black void, painterly digital art, no text",
    },
    {
        "id": "boss_hollow_prince",
        "name": "The Hollow Prince",
        "prompt": "Cinematic dark fantasy boss splash art 16:9: an elegant but cracked porcelain-faced prince with dark tears in a ruined throne room, painterly digital art, no text",
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
