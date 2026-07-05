# SwordJin

A mobile-first action RPG built in Godot 4.4, deployed as a Progressive Web App. Adapted from a 200+ chapter manhwa storyline into discrete combat and story chapters.

**Current version:** v0.34 — Act 1 (3 chapters playable)

## Play now

Open the PWA in a modern browser:

**https://kirkforge.github.io/Sword-jin_PWA-main/**

To install on mobile or desktop:

1. Open the link above in **Chrome**, **Edge**, or **Samsung Internet**.
2. Tap the **Add to Home Screen** / **Install** prompt, or choose it from the browser menu.
3. Launch the icon — the game runs full-screen and works offline after the first load.

> Safari on iOS: tap the **Share** button → **Add to Home Screen**.
> Firefox: supports PWA install on Android; on desktop use the address-bar install icon.

## Controls

| Input | Action |
|-------|--------|
| WASD / touch D-pad | Move |
| Space / tap | Attack |
| C | Chapter select |
| M | Mute |
| R | Restart chapter |

## Stack

| Layer | Choice |
|-------|--------|
| Engine | Godot 4.4.1-stable (GL Compatibility) |
| Target | Mobile PWA (HTML5 export + service worker) |
| Resolution | 640×360, scales to device |
| Save | IndexedDB (web), JSON chapter state |
| Assets | AI-generated via MiniMax (BGM, SFX, art, voice) |

## Quick Start (development)

Requires Godot 4.4.1-stable. Open `project.godot` and run from the editor.

Export the PWA locally:

```bash
godot --headless --path . --export-release "HTML5" builds/web/index.html
bash scripts/patch_pwa.sh
python3 -m http.server 8080 --directory builds/web
```

Then open http://localhost:8080.

## CI / Deployment

- Pushes to `dev` run lint, HTML5 export, and a headless gameplay smoke test.
- Pushes to `main` additionally deploy the build to GitHub Pages via `.github/workflows/ci.yml`.
- Enable GitHub Pages in the repo settings: **Settings → Pages → Source = GitHub Actions**.

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
