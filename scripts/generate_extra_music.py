#!/usr/bin/env python3
"""
generate_extra_music.py
Generate additional MiniMax music-2.6 tracks for acts, ambience, and stings.
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
        "name": "bgm_ambient_ruins",
        "prompt": "Sparse dark fantasy ambient music, distant wind through stone ruins, subtle low strings, eerie but calm, loopable, no percussion",
        "is_instrumental": True,
    },
    {
        "name": "bgm_ambient_foreboding",
        "prompt": "Slow-building dark fantasy tension ambience, low drones, distant bells, uneasy atmosphere, loopable",
        "is_instrumental": True,
    },
    {
        "name": "bgm_exploration",
        "prompt": "Medium-tempo dark fantasy exploration music, gentle strings and harp, mysterious melody, adventurous but cautious, loopable",
        "is_instrumental": True,
    },
    {
        "name": "bgm_siege",
        "prompt": "Epic dark fantasy siege music, thunderous drums, brass fanfares, marching rhythm, intense battle energy, loopable",
        "is_instrumental": True,
    },
    {
        "name": "bgm_void",
        "prompt": "Ethereal dark fantasy void music, shimmering synth pads, reversed strings, cosmic dread, dreamlike and haunting, loopable",
        "is_instrumental": True,
    },
    {
        "name": "bgm_final_confrontation",
        "prompt": "Climactic dark fantasy final boss music, choir, massive drums, fast strings, apocalyptic and heroic, loopable",
        "is_instrumental": True,
    },
    {
        "name": "bgm_triumphant",
        "prompt": "Short victorious dark fantasy fanfare, bright brass, lifting strings, celebration after battle, 15 seconds",
        "is_instrumental": True,
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
        raise RuntimeError("ffmpeg not found")


def convert_to_ogg(mp3_path: Path, ogg_path: Path):
    cmd = [
        "ffmpeg", "-y", "-i", str(mp3_path),
        "-c:a", "libvorbis", "-q:a", "4",
        str(ogg_path),
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def save_audio(data_or_url, name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mp3_path = OUT_DIR / f"{name}.mp3"
    ogg_path = OUT_DIR / f"{name}.ogg"

    # Case 1: URL string
    if isinstance(data_or_url, str) and data_or_url.startswith(("http://", "https://")):
        r = requests.get(data_or_url, stream=True, timeout=180)
        r.raise_for_status()
        with open(mp3_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    # Case 2: base64 bytes
    elif isinstance(data_or_url, (bytes, bytearray)):
        mp3_path.write_bytes(bytes(data_or_url))
    else:
        raise RuntimeError(f"Unrecognized audio payload type: {type(data_or_url)}")

    print(f"  Downloaded {mp3_path.name} ({mp3_path.stat().st_size} bytes)")
    convert_to_ogg(mp3_path, ogg_path)
    print(f"  Converted -> {ogg_path.name} ({ogg_path.stat().st_size} bytes)")
    mp3_path.unlink(missing_ok=True)
    return ogg_path


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
        "is_instrumental": track.get("is_instrumental", True),
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3",
        },
        "output_format": "url",
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
    resp.raise_for_status()

    # MiniMax may return JSON or raw binary depending on output_format
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
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
            raise RuntimeError(f"No audio URL in response: {json.dumps(data, indent=2)[:500]}")
        save_audio(audio_url, name)
    else:
        # Raw binary response
        print("  Received raw audio binary from MiniMax")
        save_audio(resp.content, name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true")
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    api_key = load_api_key()
    print("Loaded MiniMax API key.")
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
        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()
