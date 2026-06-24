#!/usr/bin/env python3
"""
generate_ui_voice_clips.py
Generate short utility narration voice clips for Swordjin UI moments.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs Ogg Vorbis to assets/sfx/voice/
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

API_KEY_PATH = Path("/home/kirk/Madlab/Lockdown/.minimax")
OUT_DIR = Path(__file__).parent.parent / "assets" / "sfx" / "voice"
API_URL = "https://api.minimax.io/v1/t2a_v2"
VOICE_ID = "English_expressive_narrator"

UI_LINES = [
    ("game_over", "The blade falls. Rise again."),
    ("daily_complete", "Daily challenge conquered."),
    ("achievement_unlocked", "A new badge shines."),
    ("level_up", "Strength renewed."),
    ("weapon_unlocked", "A new weapon answers your call."),
    ("victory", "Victory is yours."),
    ("boss_approaches", "A terrible foe draws near."),
]


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


def ensure_ffmpeg():
    if subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        raise RuntimeError("ffmpeg not found")


def download_url(url: str, path: Path):
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def convert_to_ogg(mp3_path: Path, ogg_path: Path):
    cmd = ["ffmpeg", "-y", "-i", str(mp3_path), "-c:a", "libvorbis", "-q:a", "4", str(ogg_path)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def generate_voice(name: str, text: str, api_key: str, force: bool = False):
    ogg_path = OUT_DIR / f"{name}.ogg"
    if ogg_path.exists() and not force:
        print(f"Skipping {name}")
        return

    print(f"\nGenerating voice: {name}")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "speech-2.8-hd",
        "text": text,
        "stream": False,
        "output_format": "url",
        "voice_setting": {
            "voice_id": VOICE_ID,
            "speed": 1,
            "vol": 1,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    audio_url = None
    if isinstance(data, dict):
        if "audio_url" in data:
            audio_url = data["audio_url"]
        if not audio_url and "data" in data and isinstance(data["data"], dict):
            audio_url = data["data"].get("audio") or data["data"].get("audio_url")
        if not audio_url and "file" in data and isinstance(data["file"], dict):
            audio_url = data["file"].get("download_url") or data["file"].get("audio_url") or data["file"].get("audio")

    if not audio_url:
        raise RuntimeError(f"No audio URL in response: {json.dumps(data, indent=2)}")

    mp3_path = OUT_DIR / f"{name}.mp3"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    download_url(audio_url, mp3_path)
    convert_to_ogg(mp3_path, ogg_path)
    mp3_path.unlink(missing_ok=True)
    print(f"  Saved {ogg_path.name} ({ogg_path.stat().st_size} bytes)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true")
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    api_key = load_api_key()
    ensure_ffmpeg()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    only_set = set(args.only.split(",")) if args.only else None

    for name, text in UI_LINES:
        if only_set and name not in only_set:
            continue
        try:
            generate_voice(name, text, api_key, force=args.regenerate)
        except Exception as e:
            print(f"  ERROR {name}: {e}", file=sys.stderr)
        time.sleep(0.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
