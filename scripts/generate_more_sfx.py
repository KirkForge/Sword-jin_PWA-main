#!/usr/bin/env python3
"""
generate_more_sfx.py
Generate additional procedural placeholder SFX for Swordjin.
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


def metallic_clink(freqs, duration=0.12, amplitude=0.35):
    out = []
    for freq in freqs:
        out += tone_with_decay(freq, duration / len(freqs), amplitude)
    return out


# Magic cast — ringing chime with airy tail
cast = []
for freq in [880, 1100, 1320]:
    cast += tone_with_decay(freq, 0.08, 0.25)
cast += noise(0.15, 0.08)
write_wav("magic_cast.wav", cast)

# Fire burst — noise sweep + low thud
fire = []
fire += noise(0.18, 0.45)
fire += tone_with_decay(90, 0.15, 0.5)
write_wav("fire_burst.wav", fire)

# Ice shard — glassy ping with crystalline decay
ice = []
for freq in [1200, 1600, 2000]:
    ice += tone_with_decay(freq, 0.06, 0.3)
write_wav("ice_shard.wav", ice)

# Lightning zap — buzzy descending pulse
zap = []
for freq in range(1200, 400, -80):
    zap += pulse(freq, 0.015, 0.4, 0.45)
zap += noise(0.08, 0.25)
write_wav("lightning_zap.wav", zap)

# Healing light — warm ascending chime
heal = []
for freq in [523, 659, 784, 1047]:
    heal += tone_with_decay(freq, 0.14, 0.3)
write_wav("healing_light.wav", heal)

# Poison hiss — bubbling noise with low gurgle
poison = []
poison += noise(0.2, 0.25)
poison += sine_tone(200, 0.2, 0.15)
write_wav("poison_hiss.wav", poison)

# Shield buff — resonant hum + shimmer
shield = []
shield += sine_tone(440, 0.2, 0.25)
for freq in [880, 1320]:
    shield += tone_with_decay(freq, 0.08, 0.2)
write_wav("shield_buff.wav", shield)

# Coin clink — bright short metallic pings
coin = []
coin += metallic_clink([1800, 2400, 1200], 0.1, 0.3)
write_wav("coin_clink.wav", coin)

# Chest open — creaky wood + metallic latch
chest = []
chest += noise(0.15, 0.2)
chest += metallic_clink([600, 900], 0.1, 0.25)
write_wav("chest_open.wav", chest)

# Error/deny — low discordant buzz
deny = []
deny += pulse(150, 0.18, 0.3, 0.4)
deny += pulse(120, 0.12, 0.3, 0.4)
write_wav("ui_deny.wav", deny)

# Equip/upgrade — satisfying anvil-like thud + chime
equip = []
equip += tone_with_decay(220, 0.1, 0.4)
equip += metallic_clink([660, 880], 0.08, 0.25)
write_wav("equip_item.wav", equip)

# Boss roar — low growl sweep
roar = []
for freq in range(80, 160, 4):
    roar += sine_tone(freq, 0.005, 0.5)
roar += noise(0.25, 0.35)
write_wav("boss_roar.wav", roar)

print("✅ All additional SFX generated in", OUTPUT_DIR)
