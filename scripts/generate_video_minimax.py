#!/usr/bin/env python3
"""
generate_video_minimax.py
Generate short cinematic video clips with MiniMax.
Reads API key from /home/kirk/Madlab/Lockdown/.minimax
Saves MP4 (and optionally WebM) to assets/video/
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
OUT_DIR = Path(__file__).parent.parent / "assets" / "video"
CREATE_URL = "https://api.minimax.io/v1/video_generation"
QUERY_URL = "https://api.minimax.io/v1/query/video_generation"
RETRIEVE_URL = "https://api.minimax.io/v1/files/retrieve"

VIDEOS = [
    {
        "name": "title_cinematic",
        "model": "MiniMax-Hailuo-2.3",
        "duration": 6,
        "resolution": "1080P",
        "prompt": "Cinematic dark fantasy title intro: a lone warrior draws a glowing cursed sword at sunset, wind sweeping through a ruined battlefield, banners fluttering, raven taking flight, dramatic camera slow push-in, epic atmosphere, 16:9",
    },
    {
        "name": "act3_betrayal_intro",
        "model": "MiniMax-Hailuo-2.3",
        "duration": 6,
        "resolution": "1080P",
        "prompt": "Cinematic dark fantasy scene: crimson cloaked assassins appear from shadow in a torch-lit ravine, a robed cultist raises bound wraiths from a stone altar, mist and embers, ominous ritual, 16:9",
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


def download_url(url: str, path: Path):
    r = requests.get(url, stream=True, timeout=300)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def convert_to_webm(mp4_path: Path, webm_path: Path):
    cmd = [
        "ffmpeg", "-y", "-i", str(mp4_path),
        "-c:v", "libvpx-vp9", "-b:v", "2M",
        "-c:a", "libopus",
        str(webm_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def create_task(video: dict, api_key: str) -> str:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": video["model"],
        "prompt": video["prompt"],
        "duration": video["duration"],
        "resolution": video["resolution"],
    }
    resp = requests.post(CREATE_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    task_id = data.get("task_id") or (data.get("data", {}).get("task_id"))
    if not task_id:
        raise RuntimeError(f"No task_id in response: {json.dumps(data, indent=2)}")
    return task_id


def poll_task(task_id: str, api_key: str, timeout: int = 600):
    headers = {"Authorization": f"Bearer {api_key}"}
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(QUERY_URL, headers=headers, params={"task_id": task_id}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status") or data.get("data", {}).get("status", "")
        print(f"  task {task_id[:8]}... status: {status}")
        if status == "Success":
            file_id = data.get("file_id") or data.get("data", {}).get("file_id")
            return file_id
        if status == "Fail":
            raise RuntimeError(f"Video task failed: {data}")
        time.sleep(10)
    raise RuntimeError("Video generation timed out")


def retrieve_download_url(file_id: str, api_key: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.get(RETRIEVE_URL, headers=headers, params={"file_id": file_id}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    url = data.get("file", {}).get("download_url")
    if not url:
        raise RuntimeError(f"No download_url in retrieve response: {data}")
    return url


def generate_video(video: dict, api_key: str, force: bool = False, make_webm: bool = True):
    name = video["name"]
    mp4_path = OUT_DIR / f"{name}.mp4"
    if mp4_path.exists() and not force:
        print(f"Skipping {name} (exists)")
        return

    print(f"\nGenerating video: {name}")
    task_id = create_task(video, api_key)
    print(f"  Task ID: {task_id}")
    file_id = poll_task(task_id, api_key)
    print(f"  File ID: {file_id}")
    url = retrieve_download_url(file_id, api_key)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    download_url(url, mp4_path)
    print(f"  Saved MP4: {mp4_path.name} ({mp4_path.stat().st_size} bytes)")
    if make_webm:
        webm_path = OUT_DIR / f"{name}.webm"
        convert_to_webm(mp4_path, webm_path)
        print(f"  Saved WebM: {webm_path.name} ({webm_path.stat().st_size} bytes)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true")
    parser.add_argument("--webm", action="store_true", default=True)
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    api_key = load_api_key()
    ensure_ffmpeg()
    only_set = set(args.only.split(",")) if args.only else None

    for video in VIDEOS:
        if only_set and video["name"] not in only_set:
            continue
        try:
            generate_video(video, api_key, force=args.regenerate, make_webm=args.webm)
        except Exception as e:
            print(f"  ERROR {video['name']}: {e}", file=sys.stderr)

    print("\nDone.")


if __name__ == "__main__":
    main()
