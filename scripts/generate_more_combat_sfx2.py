#!/usr/bin/env python3
"""
generate_more_combat_sfx2.py
Generate additional procedural combat, enemy, and impact SFX for Swordjin.
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


# Greatsword swing — slow heavy swoosh
write_wav("greatsword_swing.wav", swoosh(0.28, 0.45))

# Dagger stab — quick sharp puncture
stab = []
stab += noise(0.03, 0.2)
stab += tone_with_decay(1200, 0.04, 0.3)
write_wav("dagger_stab.wav", stab)

# Hammer slam — deep impact
hammer = []
hammer += noise(0.15, 0.55)
hammer += tone_with_decay(120, 0.25, 0.5)
write_wav("hammer_slam.wav", hammer)

# Spear thrust — piercing zip
spear = []
spear += noise(0.04, 0.2)
spear += swoosh(0.12, 0.25)
write_wav("spear_thrust.wav", spear)

# Fire burst — short explosive ignition
fire = []
fire += noise(0.25, 0.5)
for freq in [200, 300, 450]:
    fire += tone_with_decay(freq, 0.06, 0.35)
write_wav("fire_burst.wav", fire)

# Ice crack — brittle shatter
ice = []
for freq in [800, 1200, 1600, 2000]:
    ice += tone_with_decay(freq, 0.03, 0.25)
ice += noise(0.15, 0.2)
write_wav("ice_crack.wav", ice)

# Lightning zap — electric snap
zap = []
for i in range(8):
    zap += noise(0.02, 0.4)
    zap += tone_with_decay(1600 + i * 200, 0.03, 0.3)
write_wav("lightning_zap.wav", zap)

# Heal chime — rising warm tones
heal = []
for freq in [440, 554, 659, 880, 1100]:
    heal += tone_with_decay(freq, 0.08, 0.28)
write_wav("heal_chime.wav", heal)

# Poison proc — bubbling hiss
poison = []
for i in range(12):
    poison += noise(0.04, 0.15 + random.random() * 0.1)
write_wav("poison_proc.wav", poison)

# Bone shatter — dry crack impact
bones = []
bones += noise(0.08, 0.35)
for freq in [600, 900, 1400]:
    bones += tone_with_decay(freq, 0.03, 0.25)
write_wav("bone_shatter.wav", bones)

# Ghost wail — ethereal spectral moan
wail = []
for t in range(int(SAMPLE_RATE * 0.6)):
    env = 1.0 - abs((t / (SAMPLE_RATE * 0.6)) * 2 - 1)
    freq = 400 + math.sin(2 * math.pi * 3 * t / SAMPLE_RATE) * 100
    wail.append(0.25 * 32767 * env * math.sin(2 * math.pi * freq * t / SAMPLE_RATE))
write_wav("ghost_wail.wav", wail)

# Chain rattle — rattling metal
chain = []
for i in range(20):
    chain += noise(0.03, 0.2 + random.random() * 0.1)
    chain += metallic_clink([400 + i * 50], 0.02, 0.2)
write_wav("chain_rattle.wav", chain)

# Shield charge — heavy footfalls + impact charge
charge = []
charge += pulse(100, 0.25, 0.3, 0.5)
charge += noise(0.15, 0.45)
write_wav("shield_charge.wav", charge)

# Magic barrier up — crystalline ascending wall
barrier = []
for freq in [330, 440, 554, 659, 880, 1100]:
    barrier += tone_with_decay(freq, 0.07, 0.25)
write_wav("barrier_up.wav", barrier)

# Armor break — shearing metal
armor = []
armor += noise(0.18, 0.5)
armor += metallic_clink([250, 400, 700], 0.1, 0.4)
write_wav("armor_break.wav", armor)

# Level up fanfare — short triumphant chime
levelup = []
for freq in [523, 659, 784, 1047]:
    levelup += tone_with_decay(freq, 0.12, 0.3)
write_wav("level_up.wav", levelup)

print("✅ All additional combat SFX generated in", OUTPUT_DIR)
