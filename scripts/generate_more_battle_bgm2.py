#!/usr/bin/env python3
"""
generate_more_battle_bgm2.py
Generate additional battle/tension/dungeon BGM loops for Swordjin using MiniMax music-2.6.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Outputs Ogg Vorbis to assets/bgm/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "bgm"
API_URL = "https://api.minimax.io/v1/music_generation"

TRACKS = [
    {
        "name": "bgm_war_council",
        "prompt": "Dark fantasy war council music, muted military drums, tense low strings, strategic anticipation, loopable instrumental",
    },
    {
        "name": "bgm_foe_at_the_gate",
        "prompt": "Dark fantasy siege tension music, heavy war horns, approaching army rhythm, grim determination, loopable instrumental",
    },
    {
        "name": "bgm_inferno_rising",
        "prompt": "Dark fantasy fire-battle music, roaring brass, blazing strings, volcanic fury, loopable instrumental",
    },
    {
        "name": "bgm_howling_depths",
        "prompt": "Dark fantasy deep dungeon battle music, distant howls, low drones, cavernous percussion, loopable instrumental",
    },
    {
        "name": "bgm_unchained_vengeance",
        "prompt": "Dark fantasy revenge combat music, driving galloping rhythm, furious violins, heroic wrath, loopable instrumental",
    },
    {
        "name": "bgm_throne_room_duel",
        "prompt": "Dark fantasy climactic duel music, clashing high strings, imperial drums, one-on-one boss tension, loopable instrumental",
    },
    {
        "name": "bgm_pyre_of_legion",
        "prompt": "Dark fantasy undead legion battle music, ghostly choir pads, rattling percussion, spectral warfare, loopable instrumental",
    },
    {
        "name": "bgm_last_breath",
        "prompt": "Dark fantasy desperate final stand music, fragile piano under swelling strings, bittersweet courage, loopable instrumental",
    },
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
        raise RuntimeError("ffmpeg not found; install it to convert MP3 to OGG")


def download_url(url: str, path: Path, chunk_size: int = 8192):
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)


def convert_to_ogg(mp3_path: Path, ogg_path: Path):
    cmd = [
        "ffmpeg", "-y", "-i", str(mp3_path),
        "-c:a", "libvorbis", "-q:a", "4",
        str(ogg_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def generate_track(track: dict, api_key: str, force: bool = False):
    name = track["name"]
    ogg_path = OUT_DIR / f"{name}.ogg"
    if ogg_path.exists() and not force:
        print(f"Skipping {name} (exists)")
        return

    print(f"\nGenerating {name} ...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "music-2.6",
        "prompt": track["prompt"],
        "is_instrumental": True,
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3",
        },
        "output_format": "url",
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
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
    print(f"  Downloaded {mp3_path.name} ({mp3_path.stat().st_size} bytes)")

    convert_to_ogg(mp3_path, ogg_path)
    print(f"  Converted -> {ogg_path.name} ({ogg_path.stat().st_size} bytes)")

    mp3_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true", help="Regenerate existing tracks")
    parser.add_argument("--only", type=str, default="", help="Comma separated track names to generate")
    args = parser.parse_args()

    api_key = load_api_key()
    ensure_ffmpeg()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    only_set = set(args.only.split(",")) if args.only else None

    for track in TRACKS:
        if only_set and track["name"] not in only_set:
            continue
        try:
            generate_track(track, api_key, force=args.regenerate)
        except Exception as e:
            print(f"  ERROR {track['name']}: {e}", file=sys.stderr)
            continue
        time.sleep(1.0)

    print("\nDone.")


if __name__ == "__main__":
    main()
