# SwordJin

A mobile-first action RPG built in Godot 4.4, deployed as a Progressive Web App. Adapted from a 200+ chapter manhwa storyline into discrete combat and story chapters.

**Current version:** v0.34 — Act 1 (3 chapters playable)

## Stack

| Layer | Choice |
|-------|--------|
| Engine | Godot 4.4.1-stable (GL Compatibility) |
| Target | Mobile PWA (HTML5 export + service worker) |
| Resolution | 640×360, scales to device |
| Save | IndexedDB (web), JSON chapter state |
| Assets | AI-generated via MiniMax (BGM, SFX, art, voice) |

## Quick Start

Requires Godot 4.4.1. Open `project.godot`, run from editor.

For PWA deployment:
```bash
# After HTML5 export from Godot:
cd scripts
./patch_pwa.sh
```

## Controls

| Input | Action |
|-------|--------|
| WASD / touch D-pad | Move |
| Space / tap | Attack |
| C | Chapter select |
| M | Mute |
| R | Restart chapter |

## Asset Generation

`scripts/` contains Python generators for BGM, SFX, art, and voice clips via the MiniMax API. API key is read from `~/Madlab/Lockdown/.minimax` — not committed. Run individual scripts as needed; outputs land in `assets/`.

## Project Layout

```
project.godot       Godot project root
scenes/             Scene files (.tscn)
scripts/            GDScript autoloads + systems; Python asset generators
chapters/           Per-chapter JSON + scene references
assets/             Art, BGM, SFX, voice (generated; not all committed)
builds/web/         HTML5 export output (gitignored build artifacts)
docs/adr/           Architecture decision records
```

## Status

Act 1 (chapters 1–3) is playable. Combat, save/load, chapter select, boss fight, and audio are working. Acts 2–10 are planned; see `docs/adr/` and `ARCHITECTURE.md` for the roadmap.
