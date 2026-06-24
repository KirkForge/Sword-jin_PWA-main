#!/usr/bin/env python3
"""
generate_more_combat_sfx.py
Generate additional procedural combat and UI SFX for Swordjin.
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


def explosion(duration=0.4, amplitude=0.5):
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        env = (1.0 - t / n) ** 2
        out.append(amplitude * 32767 * env * (random.random() * 2 - 1))
    return out


def swoosh(duration=0.25, amplitude=0.35):
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        freq = 600 + (t / n) * 600
        env = 1.0 - abs((t / n) * 2 - 1)
        out.append(amplitude * 32767 * env * math.sin(2 * math.pi * freq * t / SAMPLE_RATE))
    return out


# Sword swing — quick swoosh
write_wav("sword_swing.wav", swoosh(0.18, 0.4))

# Axe hit — heavy impact + metal bite
axe = []
axe += noise(0.12, 0.5)
axe += metallic_clink([300, 450], 0.08, 0.3)
write_wav("axe_hit.wav", axe)

# Arrow shot — short string snap + zip
arrow = []
arrow += noise(0.05, 0.25)
arrow += swoosh(0.15, 0.2)
write_wav("arrow_shot.wav", arrow)

# Magic shield block — crystalline shimmer block
shield_block = []
for freq in [440, 660, 880, 1100]:
    shield_block += tone_with_decay(freq, 0.05, 0.25)
shield_block += noise(0.08, 0.15)
write_wav("shield_block.wav", shield_block)

# Critical hit — bright power spike
crit = []
for freq in [880, 1100, 1320, 1760]:
    crit += tone_with_decay(freq, 0.04, 0.3)
crit += noise(0.1, 0.25)
write_wav("critical_hit.wav", crit)

# Enemy death — gurgling fade
death = []
for freq in range(200, 80, -10):
    death += tone_with_decay(freq, 0.015, 0.3)
death += noise(0.2, 0.25)
write_wav("enemy_death.wav", death)

# Buff start — ascending chime
buff = []
for freq in [330, 440, 554, 659, 880]:
    buff += tone_with_decay(freq, 0.08, 0.28)
write_wav("buff_start.wav", buff)

# Debuff apply — descending dissonant
snare = []
for freq in [660, 523, 415, 330, 247]:
    snare += tone_with_decay(freq, 0.1, 0.28)
write_wav("debuff_apply.wav", snare)

# Stun hit — ringing bell + impact
stun = []
for freq in [1000, 1500, 2000]:
    stun += tone_with_decay(freq, 0.06, 0.3)
stun += noise(0.08, 0.2)
write_wav("stun_hit.wav", stun)

# Footstep — soft thud
step = noise(0.06, 0.25)
write_wav("footstep.wav", step)

# Door open heavy — wood creak + stone grind
door = []
door += noise(0.2, 0.2)
door += tone_with_decay(80, 0.15, 0.35)
write_wav("door_heavy.wav", door)

# UI confirm — pleasant high chime
confirm = []
for freq in [523, 659, 784]:
    confirm += tone_with_decay(freq, 0.08, 0.25)
write_wav("ui_confirm.wav", confirm)

print("✅ All additional combat SFX generated in", OUTPUT_DIR)
