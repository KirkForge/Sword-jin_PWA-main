#!/usr/bin/env python3
"""
generate_more_magic_sfx.py
Generate additional procedural magic, environment, and UI SFX for Swordjin.
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


def swoosh(duration=0.25, amplitude=0.35):
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        freq = 600 + (t / n) * 600
        env = 1.0 - abs((t / n) * 2 - 1)
        out.append(amplitude * 32767 * env * math.sin(2 * math.pi * freq * t / SAMPLE_RATE))
    return out


def magic_chime(freqs, duration=0.08, amplitude=0.35):
    out = []
    for freq in freqs:
        out += tone_with_decay(freq, duration, amplitude)
    return out


def riser(duration=0.4, amplitude=0.4):
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        freq = 200 + (t / n) * 600
        env = t / n
        out.append(amplitude * 32767 * env * math.sin(2 * math.pi * freq * t / SAMPLE_RATE))
    return out


def drop(duration=0.5, amplitude=0.4):
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        freq = 800 - (t / n) * 600
        env = (1.0 - t / n) ** 1.5
        out.append(amplitude * 32767 * env * math.sin(2 * math.pi * freq * t / SAMPLE_RATE))
    return out


# Fireball — whoosh + explosive crack
fireball = []
fireball += swoosh(0.25, 0.25)
fireball += noise(0.15, 0.55)
write_wav("fireball_cast.wav", fireball)

# Ice shard — crystalline ping + shatter
ice = []
for freq in [1200, 1600, 2000, 2400]:
    ice += tone_with_decay(freq, 0.05, 0.3)
ice += noise(0.12, 0.25)
write_wav("ice_shard.wav", ice)

# Lightning zap — sharp pulse + noise tail
lightning = []
lightning += pulse(1200, 0.08, 0.3, 0.5)
lightning += noise(0.18, 0.35)
write_wav("lightning_zap.wav", lightning)

# Heal — ascending soft chime
heal = []
for freq in [440, 554, 659, 880, 1100]:
    heal += tone_with_decay(freq, 0.09, 0.28)
write_wav("heal_cast.wav", heal)

# Poison cloud — bubbling low noise
poison = []
for i in range(8):
    poison += noise(0.06, 0.15 + i * 0.02)
write_wav("poison_cloud.wav", poison)

# Teleport — shimmering riser + sparkle
teleport = []
teleport += riser(0.3, 0.3)
teleport += magic_chime([880, 1320, 1760], 0.05, 0.25)
write_wav("teleport.wav", teleport)

# Thunder rumble — low noise swell
thunder = []
for t in range(int(SAMPLE_RATE * 0.6)):
    env = (1.0 - t / (SAMPLE_RATE * 0.6)) ** 2
    thunder.append(0.5 * 32767 * env * (random.random() * 2 - 1))
write_wav("thunder_rumble.wav", thunder)

# Wind gust — filtered noise sweep
wind = []
for t in range(int(SAMPLE_RATE * 0.5)):
    env = 1.0 - abs((t / (SAMPLE_RATE * 0.5)) * 2 - 1)
    wind.append(0.3 * 32767 * env * (random.random() * 2 - 1))
write_wav("wind_gust.wav", wind)

# UI deny — descending dissonant blip
deny = []
for freq in [330, 277, 220]:
    deny += tone_with_decay(freq, 0.1, 0.3)
write_wav("ui_deny.wav", deny)

# Level up — triumphant ascending fanfare
levelup = []
for freq in [523, 659, 784, 1047, 1319]:
    levelup += tone_with_decay(freq, 0.12, 0.3)
write_wav("level_up.wav", levelup)

# Item discovery — bright magical glint
item = []
item += magic_chime([987, 1319, 1760, 2637], 0.04, 0.3)
write_wav("item_discovery.wav", item)

# Trap trigger — sudden snap + drop
trap = []
trap += noise(0.06, 0.4)
trap += drop(0.25, 0.3)
write_wav("trap_trigger.wav", trap)

print("✅ All additional magic/environment SFX generated in", OUTPUT_DIR)
