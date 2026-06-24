#!/usr/bin/env python3
"""
generate_chapter_backgrounds.py
Batch-generate chapter background + title card art for Swordjin using MiniMax image-01.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs webp images to assets/art/bg/
"""

import base64
import json
import os
import re
import sys
import time
from io import BytesIO
from pathlib import Path


def safe_filename(title: str) -> str:
    base = title.lower().replace(' ', '_')
    return re.sub(r"[^a-z0-9_\.]", "", base)

import requests
from PIL import Image, ImageDraw, ImageFont

API_KEY_PATH = Path("/home/kirk/Madlab/Lockdown/.minimax")
OUT_DIR = Path(__file__).parent.parent / "assets" / "art" / "bg"
API_URL = "https://api.minimax.io/v1/image_generation"
RESOLUTION = (640, 360)

# Chapters 11-30: map chapter_id -> prompt + theme
CHAPTERS = [
    {
        "id": "act03_ch011",
        "idx": 11,
        "title": "The Betrayer's Blade",
        "theme": "dark_fortress",
        "prompt": "A dark fantasy RPG chapter background: a stone watchtower at twilight where a road splits, torches flickering, red-cloaked assassins waiting in shadow, mist rolling over broken signs, ominous mood, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act03_ch012",
        "idx": 12,
        "title": "Crimson's Hollow",
        "theme": "dark_fortress",
        "prompt": "A dark fantasy RPG chapter background: a sunken chapel in a ravine at midnight, ghostly wraiths bound to a blood-red altar, robed cultists chanting in a circle, incense smoke and iron mist, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act03_ch013",
        "idx": 13,
        "title": "The Shattered Vow",
        "theme": "field",
        "prompt": "A dark fantasy RPG chapter background: a muddy merchant road during a thunderstorm, abandoned wagon, assassins in crimson cloaks advancing through rain, broken vow atmosphere, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act03_ch014",
        "idx": 14,
        "title": "The Fang Priest",
        "theme": "iron_throne",
        "prompt": "A dark fantasy RPG chapter background: a Crimson Fang priest standing on a roadside shrine, cult banners flapping, bound wraiths kneeling, iron torches, grim ritual, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act03_ch015",
        "idx": 15,
        "title": "The Road South",
        "theme": "field",
        "prompt": "A dark fantasy RPG chapter background: a southern mountain pass at dusk, a merchant caravan breaking through a Crimson Fang blockade, dust and torchlight, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act04_ch016",
        "idx": 16,
        "title": "The Imperial Seal",
        "theme": "fortress",
        "prompt": "A dark fantasy RPG chapter background: an imperial fortress gate, a gate warden offering a glowing commission seal, banners of gold and blue, ceremonial atmosphere, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act04_ch017",
        "idx": 17,
        "title": "The Frontier Camp",
        "theme": "field",
        "prompt": "A dark fantasy RPG chapter background: an imperial supply camp at night under stars, tents burning, Crimson Fang raiders silhouetted against fires, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act04_ch018",
        "idx": 18,
        "title": "The Bandit King's Surrender",
        "theme": "dark_fortress",
        "prompt": "A dark fantasy RPG chapter background: a bandit king kneeling before Jin in a ruined fortress hall, last warband throwing down weapons, dramatic torchlight, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act04_ch019",
        "idx": 19,
        "title": "The Alliance Marches",
        "theme": "field",
        "prompt": "A dark fantasy RPG chapter background: three-banner alliance army marching south across rolling hills, imperial, bandit, and merchant banners flying, epic scale, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act04_ch020",
        "idx": 20,
        "title": "The Capital's Shadow",
        "theme": "iron_throne",
        "prompt": "A dark fantasy RPG chapter background: the southern capital's outer fortress under siege, siege towers and ballistae, dark clouds overhead, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act05_ch021",
        "idx": 21,
        "title": "The Imperial Army Arrives",
        "theme": "iron_throne",
        "prompt": "A dark fantasy RPG chapter background: imperial legions arriving at a massive breach in city walls, soldiers charging, banners streaming, counter-siege chaos, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act05_ch022",
        "idx": 22,
        "title": "The Inner City",
        "theme": "dark_city",
        "prompt": "A dark fantasy RPG chapter background: narrow cobble streets of a besieged inner city, smoke, distant dark tower looming, civilians fleeing, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act05_ch023",
        "idx": 23,
        "title": "The Second District",
        "theme": "dark_city",
        "prompt": "A dark fantasy RPG chapter background: ruined noble district with collapsed villas, Crimson Fang banners, the dark tower closer now, eerie green light, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act05_ch024",
        "idx": 24,
        "title": "The Third District",
        "theme": "iron_throne",
        "prompt": "A dark fantasy RPG chapter background: the base of a massive obsidian tower, barricades, last defenders, storm clouds swirling at the summit, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act05_ch025",
        "idx": 25,
        "title": "The Tower's Climb",
        "theme": "iron_throne",
        "prompt": "A dark fantasy RPG chapter background: interior of a dark tower, spiral staircase wrapping around a void, crimson energy at the top, master of the Fang waiting above, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act06_ch026",
        "idx": 26,
        "title": "What Comes After",
        "theme": "void",
        "prompt": "A dark fantasy RPG chapter background: a void realm of swirling purple and black mist, ghostly visions forming and dissolving, the moment after a master's death, ethereal, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act06_ch027",
        "idx": 27,
        "title": "The First Memory",
        "theme": "void",
        "prompt": "A dark fantasy RPG chapter background: the memory of an ancient empire, golden forge glowing, the Sword of Ruin being forged by shadowed smiths, ethereal historic vision, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act06_ch028",
        "idx": 28,
        "title": "The Second Memory",
        "theme": "void",
        "prompt": "A dark fantasy RPG chapter background: a void memory of the betrayer shattering a world, cracks of light across darkness, cataclysm, ethereal and tragic, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act06_ch029",
        "idx": 29,
        "title": "The Third Memory",
        "theme": "void",
        "prompt": "A dark fantasy RPG chapter background: a prophetic vision of Jin's possible future, two paths branching in starlight, a crown of ruin and a sword set down, ethereal, painterly digital art, 16:9 game background, no text",
    },
    {
        "id": "act06_ch030",
        "idx": 30,
        "title": "The Sword Set Down",
        "theme": "iron_throne",
        "prompt": "A dark fantasy RPG chapter background: a vast throne room at dawn, Jin placing the Sword of Ruin on the steps of an empty throne, light breaking through windows, bittersweet ending, painterly digital art, 16:9 game background, no text",
    },
]


def load_api_key() -> str:
    if not API_KEY_PATH.exists():
        raise FileNotFoundError(f"API key not found at {API_KEY_PATH}")
    text = API_KEY_PATH.read_text().strip()
    # If file has multiple lines or key=value format, extract the key
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            if key.strip().lower() in ("api_key", "key", "minimax_api_key"):
                return value.strip()
        # Otherwise treat the whole line as the key if it looks like one
        if re.match(r"^sk-[A-Za-z0-9_-]+", line):
            return line
    # Fallback: return first non-empty stripped line
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


def make_title_card(background: Image.Image, chapter_idx: int, title: str) -> Image.Image:
    card = background.copy().convert("RGB")
    draw = ImageDraw.Draw(card)

    # Try to load a bold font, falling back through options
    font_size = 42
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

    chapter_text = f"Chapter {chapter_idx:02d}"

    # Dark overlay at top for readability
    overlay_height = 120
    draw.rectangle((0, 0, card.width, overlay_height), fill=(0, 0, 0, 160))

    # Text with outline shadow
    def draw_text_outlined(text, y_offset, main_color, shadow_color=(0, 0, 0)):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (card.width - text_w) // 2
        # shadow
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, 2), (0, -2), (2, 0), (-2, 0)]:
            draw.text((x + dx, y_offset + dy), text, font=font, fill=shadow_color)
        draw.text((x, y_offset), text, font=font, fill=main_color)

    draw_text_outlined(chapter_text, 24, (220, 220, 220))
    draw_text_outlined(title, 76, (255, 255, 255))

    return card


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print("Loaded MiniMax API key.")
    print(f"Output directory: {OUT_DIR}")

    for ch in CHAPTERS:
        idx = ch["idx"]
        bg_path = OUT_DIR / f"ch{idx:02d}_{safe_filename(ch['title'])}.webp"
        title_path = OUT_DIR / f"ch{idx:02d}_title.webp"

        if bg_path.exists() and title_path.exists():
            print(f"Skipping ch{idx:02d} (already exists)")
            continue

        print(f"\nGenerating ch{idx:02d} — {ch['title']}")
        try:
            img = generate_image(ch["prompt"], api_key)
            # Resize/crop to target resolution
            img.thumbnail(RESOLUTION, Image.LANCZOS)
            bg = Image.new("RGB", RESOLUTION, (10, 10, 15))
            x = (RESOLUTION[0] - img.width) // 2
            y = (RESOLUTION[1] - img.height) // 2
            bg.paste(img, (x, y))
            bg.save(bg_path, "WEBP", quality=85, method=6)
            print(f"  Saved background: {bg_path}")

            title_card = make_title_card(bg, idx, ch["title"])
            title_card.save(title_path, "WEBP", quality=85, method=6)
            print(f"  Saved title card: {title_path}")

        except Exception as e:
            print(f"  ERROR ch{idx:02d}: {e}", file=sys.stderr)
            continue

        # Small polite delay between requests
        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
