#!/usr/bin/env python3
"""
generate_more_ui_sfx.py
Generate additional procedural UI, environment, and feedback SFX for Swordjin.
Outputs WAV files to assets/sfx/
"""

import math
import os
import random
import struct
import wave

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 22050


def write_wav(filename, samples):
    path = os.path.join(OUTPUT_DIR, filename)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        for s in samples:
            w.writeframesraw(struct.pack("<h", int(max(-32767, min(32767, s)))))
    print("Generated:", path)


def sine_tone(freq: float, duration: float, amplitude: float = 0.4):
    n = int(SAMPLE_RATE * duration)
    return [amplitude * 32767 * math.sin(2 * math.pi * freq * t / SAMPLE_RATE) for t in range(n)]


def tone_with_decay(freq: float, duration: float, amplitude: float = 0.4):
    n = int(SAMPLE_RATE * duration)
    return [amplitude * 32767 * (1.0 - t / n) * math.sin(2 * math.pi * freq * t / SAMPLE_RATE) for t in range(n)]


def noise(duration: float, amplitude: float = 0.3):
    n = int(SAMPLE_RATE * duration)
    return [amplitude * 32767 * (random.random() * 2 - 1) for _ in range(n)]


def pulse(freq: float, duration: float, duty: float = 0.5, amplitude: float = 0.4):
    n = int(SAMPLE_RATE * duration)
    out = []
    period = SAMPLE_RATE / freq
    for t in range(n):
        env = 1.0 - (t / n)
        val = 1.0 if (t % period) < (period * duty) else -1.0
        out.append(amplitude * 32767 * env * val)
    return out


def click_blip(freq: float, duration: float = 0.05, amplitude: float = 0.3):
    return tone_with_decay(freq, duration, amplitude)


def tick_seq(freqs, duration_each=0.03, amplitude=0.25):
    out = []
    for freq in freqs:
        out += tone_with_decay(freq, duration_each, amplitude)
    return out


def soft_rise(duration=0.25, amplitude=0.3):
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        freq = 400 + (t / n) * 400
        env = t / n
        out.append(amplitude * 32767 * env * math.sin(2 * math.pi * freq * t / SAMPLE_RATE))
    return out


def soft_drop(duration=0.25, amplitude=0.3):
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        freq = 800 - (t / n) * 400
        env = 1.0 - t / n
        out.append(amplitude * 32767 * env * math.sin(2 * math.pi * freq * t / SAMPLE_RATE))
    return out


def shimmer(freqs, duration=0.12, amplitude=0.25):
    out = []
    for freq in freqs:
        out += tone_with_decay(freq, duration, amplitude)
    return out


# UI hover — gentle high blip
write_wav("ui_hover.wav", click_blip(880, 0.04, 0.2))

# UI select — pleasant confirm
write_wav("ui_select.wav", shimmer([523, 659, 784], 0.06, 0.25))

# UI back/cancel — descending tick
cancel = []
cancel += tick_seq([440, 330, 220], 0.04, 0.25)
write_wav("ui_back.wav", cancel)

# UI warning — urgent low pulse
warning = []
warning += pulse(300, 0.15, 0.4, 0.4)
warning += pulse(300, 0.15, 0.4, 0.4)
write_wav("ui_warning.wav", warning)

# UI error — harsh buzz
error = []
for i in range(3):
    error += pulse(150, 0.08, 0.5, 0.35)
write_wav("ui_error.wav", error)

# UI toggle — soft switch click
write_wav("ui_toggle.wav", click_blip(1200, 0.03, 0.2))

# UI page turn — paper rustle-ish noise sweep
page = []
for t in range(int(SAMPLE_RATE * 0.2)):
    env = 1.0 - abs((t / (SAMPLE_RATE * 0.2)) * 2 - 1)
    page.append(0.15 * 32767 * env * (random.random() * 2 - 1))
write_wav("ui_page_turn.wav", page)

# Quest update — bright notification fanfare
quest = []
quest += soft_rise(0.2, 0.25)
quest += shimmer([880, 1100, 1320], 0.08, 0.25)
write_wav("quest_update.wav", quest)

# Map open — mystical spatial sweep
write_wav("map_open.wav", soft_rise(0.3, 0.25))

# Coin pouch — clinking coins
pouch = []
for i in range(6):
    pouch += click_blip(2000 + i * 200, 0.03, 0.15)
write_wav("coin_pouch.wav", pouch)

# Inventory open — leather/cloth rustle + soft chime
inv = []
inv += noise(0.12, 0.15)
inv += shimmer([660, 880], 0.05, 0.2)
write_wav("inventory_open.wav", inv)

# Camp rest — fire crackle and soft sigh
rest = []
for i in range(20):
    rest += noise(0.05, 0.08 + random.random() * 0.05)
write_wav("camp_rest.wav", rest)

print("✅ All additional UI/environment SFX generated in", OUTPUT_DIR)
