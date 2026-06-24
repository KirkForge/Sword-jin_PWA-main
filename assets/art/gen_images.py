#!/usr/bin/env python3
"""Swordjin art generation via OpenRouter + Gemini 2.5 Flash Image."""

import base64, json, os, sys, time, requests

API_KEY = open(os.path.expanduser("~/.picoclaw/workspace/.openrouter")).read().strip()
MODEL = "google/gemini-2.5-flash-image"
OUT_DIR = "/home/kirk/Madlab/Clean-Live/Sword-jin_PWA/assets/art"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

STYLE = (
    "Dark fantasy wuxia 2D game art, clean pixel-art inspired style, "
    "limited palette: gold #FFD700, steel blue #5080C8, dark bg #0D1117, "
    "bone white #DCE6F0, rust #8B2500, purple #8C2E8C. "
    "No text, no letters, no words."
)

# ── All 37 prompts ──────────────────────────────────────────────────────────

PROMPTS = []

# 1. Title splash
PROMPTS.append({
    "subdir": "title",
    "filename": "title_splash.png",
    "prompt": (
        f"{STYLE} A lone swordsman (Jin) in blue tunic standing on a cliff edge at sunset, "
        "facing a dark iron fortress in the distance. His sword is drawn and raised. "
        "Wind blows his dark brown hair and tunic. Below the cliff, an army of skeletal warriors "
        "with glowing green eyes marches toward the fortress. The sky is deep navy #0D1117 with "
        "a burning orange #FF8020 sunset on the horizon. Gold #FFD700 light glints off the blade. "
        "Epic, dramatic, vertical composition."
    ),
})

# 2. Chapter backgrounds
PROMPTS.append({
    "subdir": "bg",
    "filename": "field_sunset.png",
    "prompt": (
        f"{STYLE} Wide landscape background, no characters. Open grassy field at dusk. "
        "Rolling hills of dark green #2D5A1E grass stretching to the horizon. Sky is deep navy "
        "#0D1117 at top fading to burnt orange #FF8020 at the horizon line. A few distant dead "
        "trees silhouetted. Scattered rocks #505860. Faint moonlight. Parallax-ready: foreground "
        "grass is slightly darker and more detailed, midground has gentle hills, background fades "
        "to silhouette. Horizontal 16:9 composition."
    ),
})
PROMPTS.append({
    "subdir": "bg",
    "filename": "forest_night.png",
    "prompt": (
        f"{STYLE} Wide landscape background, no characters. Dense dark forest at night. "
        "Tall gnarled trees with dark canopies #1E3A0E blocking most of the sky. Faint green "
        "#00DC00 glow from between tree roots (mushroom light). Ground is dark earth #1E2E14 "
        "with exposed roots. Occasional ghostly white #DCE6F0 wisps floating between trees. "
        "Sky barely visible through canopy, dark navy #0A0E14. Foreground has close tree trunks, "
        "midground has path through trees, background is impenetrable darkness. Spooky, claustrophobic. "
        "Horizontal 16:9 composition."
    ),
})
PROMPTS.append({
    "subdir": "bg",
    "filename": "fortress_dawn.png",
    "prompt": (
        f"{STYLE} Wide landscape background, no characters. Ancient stone fortress at dawn. "
        "Massive grey stone walls #505860 with battlements. A steel blue #5080C8 dawn sky above "
        "with thin clouds. Torches with orange #FF8020 flames on the ramparts. Gate is slightly "
        "ajar with darkness inside. Foreground: stone path and scattered rubble. Midground: "
        "fortress gate and walls. Background: mountain silhouettes in morning mist. Imposing, "
        "fortified. Horizontal 16:9 composition."
    ),
})
PROMPTS.append({
    "subdir": "bg",
    "filename": "iron_throne.png",
    "prompt": (
        f"{STYLE} Wide landscape background, no characters. Dark iron throne room interior. "
        "Massive iron gate #404858 with rust #8B2500 highlights at the far end, faintly glowing "
        "red from behind. Walls are dark iron #303848 with torch sconces casting orange #FF8020 "
        "light pools. Floor is dark stone #283040 with a long red carpet #8B2500 leading to the "
        "gate. Ceiling is lost in shadow #0D1117. Foreground: stone pillars on each side. "
        "Dramatic, ominous, final boss atmosphere. Horizontal 16:9 composition."
    ),
})

# Act 03 — Betrayal chapter backgrounds (ch011-ch015)
ACT3_BACKGROUNDS = [
    ("ch11_title", "Crimson Fang outpost at twilight. A wooden watchtower with red banners #8B2500 fluttering, a stone road leading south into dark forest. The sky is deep purple #2A0A3A fading to rust #8B2500 at the horizon. Foreground: torchlit clearing with a single bandit silhouette. Midground: watchtower and wagon debris. Background: southern road disappearing into dark forest. Ominous, hostile territory. Horizontal 16:9 composition."),
    ("ch12_title", "Sunken chapel in a ravine at midnight. A circular stone altar lit by red #8B2500 candles, surrounded by chanting cultists in dark robes #202028. Wraith silhouettes #8C2E8C float above the altar. Walls are wet stone #303038 with red moss. Floor is cracked flagstone with blood #8B2500 stains. Foreground: iron railings. Midground: altar and cultists. Background: dark ceiling lost in incense smoke. Ritualistic, horror. Horizontal 16:9 composition."),
    ("ch13_title", "Storm-lashed merchant road at night. Heavy rain #404048, lightning illuminating a red-cloaked assassin mid-leap between two wagons. Road is broken cobblestone #404048 with mud #2A1A0E. A merchant wagon lies overturned in the background, scattered goods visible. Sky is black #0D1117 with purple #8C2E8C storm clouds. Foreground: rain-soaked dirt and Jin's boot. Midground: assassin and broken wagon. Background: lightning-struck horizon. Tense, pursuit. Horizontal 16:9 composition."),
    ("ch14_title", "Crimson chapel interior, a black tower of red stone. The priest stands at an altar of bone #DCE6F0, hands raised toward three wraiths orbiting her like a constellation. Candles #FFD700 line the walls, casting long shadows. Floor is red marble #8B2500. Walls are dark stone #303038 with carved runes #8C2E8C glowing faintly. Foreground: scattered prayer beads. Midground: priest and wraith orbit. Background: arched window showing a blood moon #FF4040. Occult, climactic. Horizontal 16:9 composition."),
    ("ch15_title", "Southern mountain pass at dusk. A narrow stone road #404048 winding between two peaks, the last golden #FFD700 light of sunset on the horizon. The merchant caravan winds down the pass: three wagons, two horses, several small figures. The sky is deep navy #0D1117 above fading to gold #FFD700 at the horizon. Foreground: stone road and Jin's shadow stretching east. Midground: caravan. Background: the peaks and the southern road beyond. Hopeful, departure. Horizontal 16:9 composition."),
]

for ch_id, scene_desc in ACT3_BACKGROUNDS:
    PROMPTS.append({
        "subdir": "bg",
        "filename": f"{ch_id}.webp",
        "prompt": (
            f"{STYLE} Wide landscape background, no characters. {scene_desc}"
        ),
    })

# Act 04 — Alliance chapter backgrounds (ch016-ch020)
ACT4_BACKGROUNDS = [
    ("ch16_title", "Imperial fortress gate at dawn. A massive iron gate #404858 with a carved imperial seal #FFD700 above it, banners of three houses: merchant, imperial, and a red fang banner broken. Stone walls #303848 with morning mist. The gate warden stands at the threshold in ceremonial armor #404858. Foreground: stone road and Jin's shadow. Midground: gate and warden. Background: mountains and the southern road beyond. Honorable, threshold. Horizontal 16:9 composition."),
    ("ch17_title", "Imperial supply camp at night under attack. Tents #404048 in rows, red Fang fighters pouring over the eastern palisade, soldiers in imperial armor #404858 forming shield walls. Torches #FF8020 line the camp road. Sky is dark #0D1117 with red #8B2500 smoke from burning wagons. Foreground: a soldier's fallen helmet. Midground: shield wall and attackers. Background: treeline with red glow. Defensive, desperate. Horizontal 16:9 composition."),
    ("ch18_title", "Old bandit fortress at dusk. A crumbling stone keep #303848 on a hill, the bandit king Kaelen kneeling on one knee in the courtyard, his warband behind him. Banners of the eastern clans hang limp. Sky is deep orange #FF8020 fading to purple #2A0A3A. Foreground: a single bandit sword planted in the dirt. Midground: Kaelen kneeling, Jin standing. Background: keep silhouette. Surrender, pact. Horizontal 16:9 composition."),
    ("ch19_title", "Southern provincial road at midday, three banners marching. The merchant's wagon, the imperial standard, and the eastern bandit banner flying side by side. The road cuts through rolling hills #2A4A2A with villages of red-roofed houses in the distance. Sky is blue #4488CC with scattered clouds. Foreground: trampled grass and boot prints. Midground: the three banners. Background: southern horizon with a dark city silhouette. Triumphant, march. Horizontal 16:9 composition."),
    ("ch20_title", "Southern capital's outer fortress under siege at twilight. A massive red stone wall #8B2500 with iron portcullis #303848, two golems in front, and the alliance's three banners arrayed below. Siege ladders #404048 lean against the wall. Sky is deep crimson #8B2500 fading to black #0D1117. Foreground: a broken siege ladder and a soldier's standard. Midground: the alliance army at the wall. Background: the inner city silhouette with a single dark tower. Climactic, siege. Horizontal 16:9 composition."),
]

for ch_id, scene_desc in ACT4_BACKGROUNDS:
    PROMPTS.append({
        "subdir": "bg",
        "filename": f"{ch_id}.webp",
        "prompt": (
            f"{STYLE} Wide landscape background, no characters. {scene_desc}"
        ),
    })

# Act 05 — War chapter backgrounds (ch021-ch025)
ACT5_BACKGROUNDS = [
    ("ch21_title", "The breach at dawn with the imperial army. A thousand soldiers in steel #404858 and crimson #8B2500, banners of the throne flying, a wall of red stone broken at the center. The alliance stands at the breach. Foreground: a fallen standard. Midground: imperial soldiers and the breach. Background: the inner city silhouette. Triumphant, vast. Horizontal 16:9 composition."),
    ("ch22_title", "The first inner-city district at midday. Narrow streets #303848 with red-roofed houses #8B2500, a wraith patrol on a rooftop, barricades of broken furniture. The alliance pushes through. Foreground: an overturned cart. Midground: soldiers and barricades. Background: a necromancer on a balcony. Urban warfare. Horizontal 16:9 composition."),
    ("ch23_title", "The second district at dusk. Rune-carved streets #303848 glowing faintly purple #8C2E8C, three assassins on the rooftops, the bandit king climbing a wall. The dark tower is visible at the end of the street. Foreground: a rune glowing on the cobblestone. Midground: assassins and alliance. Background: tower silhouette. Intense, close. Horizontal 16:9 composition."),
    ("ch24_title", "The third district at twilight. A horde of wraiths #DCE6F0 with glowing eyes #8C2E8C filling the street, a golem #404858 in the foreground, the alliance at the far end. The dark tower looms above. Foreground: a wraith crawling from the cobblestones. Midground: horde and golem. Background: tower. Overwhelming. Horizontal 16:9 composition."),
    ("ch25_title", "The top of the dark tower at midnight. A single room with a forge #303848 and an altar of bone #DCE6F0. The sword Remembrance lies on the altar, glowing red #8B2500. Jin stands at the door. Foreground: the altar and sword. Midground: Jin. Background: the night sky through a broken window. Climactic, sacred. Horizontal 16:9 composition."),
]

for ch_id, scene_desc in ACT5_BACKGROUNDS:
    PROMPTS.append({
        "subdir": "bg",
        "filename": f"{ch_id}.webp",
        "prompt": (
            f"{STYLE} Wide landscape background, no characters. {scene_desc}"
        ),
    })

# Act 06 — Prophecy chapter backgrounds (ch026-ch030)
ACT6_BACKGROUNDS = [
    ("ch26_title", "The sword's first vision. A void of deep purple #2A0A3A and bone white #DCE6F0, the priest's silhouette visible in the center, surrounded by wraith-echoes. A forge temple of black stone in the distance. Foreground: the sword lying on the floor. Midground: priest silhouette. Background: forge temple. Prophetic, otherworldly. Horizontal 16:9 composition."),
    ("ch27_title", "The first wielder's memory. An ancient empire of iron #404858 and bone #DCE6F0, the first wielder as a giant wraith silhouette holding the sword. The world below is a forge of continents. Foreground: a continent being shaped. Midground: wraith-wielder. Background: the cosmos. Cosmic, scale. Horizontal 16:9 composition."),
    ("ch28_title", "The betrayer's memory. A broken empire in red #8B2500 and ash #303038, the betrayer as a wraith with a sword shattering a throne. The world cracks beneath him. Foreground: shards of a broken crown. Midground: betrayer and cracked earth. Background: a dying sun #FF8020. Destructive, ruin. Horizontal 16:9 composition."),
    ("ch29_title", "Jin's dark future. A vision of Jin as a shadow in dark armor #202028 with the sword in his hand, standing alone on a field of corpses. The merchant lies dead at his feet. Foreground: the merchant's body. Midground: dark Jin. Background: a broken throne. Prophetic, terrible. Horizontal 16:9 composition."),
    ("ch30_title", "The sword set down. The top of the tower at sunrise #FFD700. The sword lies on the altar, silent. Jin stands with his back to the altar, facing the sunrise. The merchant and bandit king stand behind him. Foreground: the sword on the altar. Midground: Jin. Background: sunrise over the inner city. Peaceful, final. Horizontal 16:9 composition."),
]

for ch_id, scene_desc in ACT6_BACKGROUNDS:
    PROMPTS.append({
        "subdir": "bg",
        "filename": f"{ch_id}.webp",
        "prompt": (
            f"{STYLE} Wide landscape background, no characters. {scene_desc}"
        ),
    })

# 3. Achievement badges
BADGES = [
    ("first_blood", "A single blood-red sword dripping"),
    ("body_count_50", "A skull pile, 3 skulls stacked"),
    ("body_count_200", "A mountain of skulls with a sword planted in it"),
    ("flawless_chapter", "A glowing blue shield with a gold star"),
    ("first_step", "A single boot stepping onto a stone path"),
    ("half_way", "A compass with the needle pointing forward"),
    ("act2_reacher", "An iron gate with a crack of red light"),
    ("act3_reacher", "A single purple eye with a wraith silhouette inside the iris"),
    ("act3_complete", "A broken red fang symbol with a gold #FFD700 sword piercing through it"),
    ("act4_reacher", "Three banners of different colors tied to a single sword pommel"),
    ("act4_complete", "A broken siege gate with three banners flying above it"),
    ("act5_reacher", "An imperial standard with a thousand swords forming a halo behind it"),
    ("act5_complete", "A dark tower collapsing with a single red wraith falling from the top"),
    ("act6_reacher", "A single purple eye with the reflection of a sword inside the iris"),
    ("act6_complete", "A sword laid across an altar of stone with a single white dove flying above"),
    ("armory_3", "Three crossed swords of different sizes"),
    ("armory_all", "Six weapons arranged in a fan (swords, daggers, bow)"),
    ("bestiary_half", "An open book with a skull bookmark"),
    ("bestiary_all", "A closed book with a glowing green eye on the cover"),
    ("speed_demon", "A lightning bolt with motion lines"),
    ("perfectionist", "Three gold stars in a triangle"),
    ("legendary_find", "A sword radiating gold beams"),
    ("combo_master", "Three overlapping slash arcs in red-orange-yellow"),
    ("first_crit", "An eye with a golden iris and crosshair pupil"),
    ("crit_50", "A bullseye target with an arrow in the center"),
    ("enraged_kill", "A red-veined fist crushing a skull"),
    ("summon_slayer", "A broken staff with purple shards scattering"),
    ("streak_3", "Three lit candles in a row"),
    ("streak_7", "Seven lit candles with the tallest in center"),
    ("daily_challenger", "A calendar page with a sword through it"),
    ("daily_veteran", "A medal with seven notches on the ribbon"),
    ("ghost_hunter", "A ghost silhouette with a blue targeting reticle"),
    ("speed_demon_5", "Five small lightning bolts in a circle"),
]

for badge_id, subject in BADGES:
    PROMPTS.append({
        "subdir": "badges",
        "filename": f"{badge_id}.png",
        "prompt": (
            f"{STYLE} Single centered achievement badge icon on dark #0D1117 background. "
            f"Circular frame with gold #FFD700 border and dark fill. Inside the circle: {subject}. "
            "Clean, readable at small size, icon-style, no background detail beyond the circle frame."
        ),
    })

# 4. Item art
ITEMS = [
    ("broken_sword", "A rusty broken sword, blade is cracked and chipped with rust #8B2500 spots, handle wrapped in dark leather #3C2D1E, lying at slight angle"),
    ("steel_dagger", "A clean short dagger, silver-white blade #C8C8D2, simple crossguard, dark wood handle #604020, point facing up"),
    ("captains_blade", "An ornate long sword, gleaming blade #E0E8F0, gold #FFD700 crossguard with scrollwork, worn leather grip #604020, ruby pommel, point facing up"),
    ("health_potion", "A glass bottle of glowing red #E04040 liquid, cork stopper, round-bottomed flask shape, faint red glow around it"),
    ("steel_sword", "A standard steel long sword, blade #D0D8E0, steel blue #5080C8 crossguard, leather-wrapped grip #3C2D1E"),
    ("gold_coin", "A single gold coin #FFD700 with a sword stamped on it, slight 3/4 rotation to show thickness, edge has reeded detail"),
]

for item_id, desc in ITEMS:
    PROMPTS.append({
        "subdir": "items",
        "filename": f"{item_id}.png",
        "prompt": (
            f"{STYLE} Single centered item on dark #0D1117 background. "
            f"Clean icon style, suitable for inventory display. No frame, no border. {desc}"
        ),
    })

# 5. Merchant portrait
PROMPTS.append({
    "subdir": "npcs",
    "filename": "merchant_portrait.png",
    "prompt": (
        f"{STYLE} Portrait of a traveling merchant, bust view, centered on dark #0D1117 background. "
        "Elderly man with weathered skin #DCB48C, wise squinting eyes. Wearing a deep purple #8C2E8C "
        "robe with gold #FFD700 trim. A wide-brimmed dark brown #644020 hat. A heavy pack over one "
        "shoulder with potion bottles and scrolls visible. Warm, mysterious, trustworthy. No frame."
    ),
})


def generate_one(idx, total, entry):
    subdir = os.path.join(OUT_DIR, entry["subdir"])
    os.makedirs(subdir, exist_ok=True)
    filepath = os.path.join(subdir, entry["filename"])

    if os.path.exists(filepath):
        print(f"[{idx+1}/{total}] SKIP (exists): {entry['subdir']}/{entry['filename']}")
        return True

    print(f"[{idx+1}/{total}] Generating: {entry['subdir']}/{entry['filename']}")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": entry["prompt"],
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ERROR request failed: {e}")
        return False

    # OpenRouter puts images in message.images[].image_url.url (data URI)
    images = data.get("choices", [{}])[0].get("message", {}).get("images", [])
    for img in images:
        url = img.get("image_url", {}).get("url", "") if isinstance(img, dict) else ""
        if url.startswith("data:image"):
            b64 = url.split(",", 1)[1]
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(b64))
            print(f"  Saved: {filepath} ({os.path.getsize(filepath)} bytes)")
            return True

    print(f"  FAILED: Could not extract image from response")
    print(f"  Response keys: {list(data.keys())}")
    if "choices" in data:
        msg = data["choices"][0].get("message", {})
        print(f"  Message keys: {list(msg.keys())}")
        print(f"  Images count: {len(msg.get('images', []))}")
        c = msg.get("content", "")
        if isinstance(c, str):
            print(f"  Content text: {c[:200]}")
    return False


def main():
    total = len(PROMPTS)
    print(f"Swordjin Art Generator — {total} images via {MODEL}")
    print(f"Output dir: {OUT_DIR}")
    print()

    success = 0
    failed = 0
    skipped = 0

    for idx, entry in enumerate(PROMPTS):
        filepath = os.path.join(OUT_DIR, entry["subdir"], entry["filename"])
        if os.path.exists(filepath):
            skipped += 1
            print(f"[{idx+1}/{total}] SKIP (exists): {entry['subdir']}/{entry['filename']}")
            continue

        ok = generate_one(idx, total, entry)
        if ok:
            success += 1
        else:
            failed += 1

        # Rate limit: be nice to the API
        if idx < total - 1:
            time.sleep(2)

    print()
    print(f"Done! Success: {success}, Failed: {failed}, Skipped: {skipped}")


if __name__ == "__main__":
    main()