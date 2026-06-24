#!/usr/bin/env python3
"""
generate_boss_splash.py
Batch-generate boss splash / portrait art for Swordjin boss chapters.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/generated/boss_splash/
"""

import base64
import json
import os
import re
import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

API_KEY_PATH = Path("/home/kirk/Madlab/Lockdown/.minimax")
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "generated" / "boss_splash"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (640, 360)


def safe_filename(title: str) -> str:
    base = title.lower().replace(" ", "_")
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


def fit_to_resolution(img: Image.Image) -> Image.Image:
    img.thumbnail(RESOLUTION, Image.LANCZOS)
    bg = Image.new("RGB", RESOLUTION, (10, 10, 15))
    x = (RESOLUTION[0] - img.width) // 2
    y = (RESOLUTION[1] - img.height) // 2
    bg.paste(img, (x, y))
    return bg


def add_title_overlay(bg: Image.Image, title: str, subtitle: str = "") -> Image.Image:
    card = bg.copy().convert("RGB")
    draw = ImageDraw.Draw(card)

    font_size = 36
    font = None
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    overlay_height = 110 if subtitle else 80
    draw.rectangle((0, 0, card.width, overlay_height), fill=(0, 0, 0, 170))

    def draw_text_outlined(text, y_offset, color=(255, 255, 255)):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (card.width - text_w) // 2
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, 2), (0, -2), (2, 0), (-2, 0)]:
            draw.text((x + dx, y_offset + dy), text, font=font, fill=(0, 0, 0))
        draw.text((x, y_offset), text, font=font, fill=color)

    draw_text_outlined(title, 20)
    if subtitle:
        small_font = None
        try:
            small_font = ImageFont.truetype(font.path, 22)
        except Exception:
            small_font = font
        bbox = draw.textbbox((0, 0), subtitle, font=small_font)
        text_w = bbox[2] - bbox[0]
        x = (card.width - text_w) // 2
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((x + dx, 70 + dy), subtitle, font=small_font, fill=(0, 0, 0))
        draw.text((x, 70), subtitle, font=small_font, fill=(220, 180, 120))
    return card


# Boss chapters in narrative order with focused cinematic prompts.
BOSSES = [
    {
        "chapter_id": "act01_ch003",
        "idx": 3,
        "title": "The Iron Gate",
        "prompt": "Dark fantasy boss splash art: a massive iron gate set in weathered stone walls, a hulking gate warden in half-plate raising a glowing key, torches blazing at dusk, dramatic low-angle shot, painterly digital art, 16:9, no text",
    },
    {
        "chapter_id": "act02_ch008",
        "idx": 8,
        "title": "The Crimson Lieutenant",
        "prompt": "Dark fantasy boss splash art: a crimson-cloaked lieutenant of the Crimson Fang standing atop a ruined battlement, dual curved blades drawn, assassins kneeling behind, stormy night sky, dramatic painterly digital art, 16:9, no text",
    },
    {
        "chapter_id": "act02_ch010",
        "idx": 10,
        "title": "The Capital Gates",
        "prompt": "Dark fantasy boss splash art: the massive bronze gates of a southern capital under siege, ballistae firing, soldiers clashing on the ramparts, smoke and banners, epic painterly digital art, 16:9, no text",
    },
    {
        "chapter_id": "act03_ch012",
        "idx": 12,
        "title": "Crimson's Hollow",
        "prompt": "Dark fantasy boss splash art: a sunken chapel altar in a ravine, a shadowy Crimson Fang ritualist summoning wraiths from a blood-red crystal, cultists chanting in a circle, mist and embers, painterly digital art, 16:9, no text",
    },
    {
        "chapter_id": "act03_ch014",
        "idx": 14,
        "title": "The Fang Priest",
        "prompt": "Dark fantasy boss splash art: a tall robed Fang Priest with a carved bone mask, raising a staff crowned with a fanged skull, bound spirits swirling around him, iron torches, painterly digital art, 16:9, no text",
    },
    {
        "chapter_id": "act04_ch020",
        "idx": 20,
        "title": "The Capital's Shadow",
        "prompt": "Dark fantasy boss splash art: the dark silhouette of a possessed noble against the backdrop of a burning capital, shadow tendrils rising, eyes glowing white, ominous painterly digital art, 16:9, no text",
    },
    {
        "chapter_id": "act05_ch025",
        "idx": 25,
        "title": "The Tower's Climb",
        "prompt": "Dark fantasy boss splash art: a spiral staircase inside a black obsidian tower, a master of the Crimson Fang waiting at the top wreathed in red lightning, vertigo-inducing perspective, painterly digital art, 16:9, no text",
    },
    {
        "chapter_id": "act06_ch030",
        "idx": 30,
        "title": "The Sword Set Down",
        "prompt": "Dark fantasy final boss splash art: an empty throne room at dawn, Jin standing before the throne with the Sword of Ruin held down at his side, golden light breaking through shattered windows, bittersweet victory, painterly digital art, 16:9, no text",
    },
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for boss in BOSSES:
        idx = boss["idx"]
        safe = safe_filename(boss["title"])
        splash_path = OUT_DIR / f"boss{idx:02d}_{safe}_splash.webp"
        portrait_path = OUT_DIR / f"boss{idx:02d}_{safe}_portrait.webp"

        if splash_path.exists() and portrait_path.exists():
            print(f"Skipping boss {idx:02d} (already exists)")
            continue

        print(f"\nGenerating boss {idx:02d} — {boss['title']}")
        try:
            img = generate_image(boss["prompt"], api_key)
            bg = fit_to_resolution(img)

            bg.save(splash_path, "WEBP", quality=85, method=6)
            print(f"  Saved splash: {splash_path}")

            titled = add_title_overlay(bg, f"Boss {idx:02d}", boss["title"])
            titled.save(portrait_path, "WEBP", quality=85, method=6)
            print(f"  Saved portrait: {portrait_path}")

        except Exception as e:
            print(f"  ERROR boss {idx:02d}: {e}", file=sys.stderr)
            continue

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
