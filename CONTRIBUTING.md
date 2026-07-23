# Contributing

## Prerequisites

- **Godot 4.4.1-stable** — not 4.4.0, not 4.5. Get it from [godotengine.org/download](https://godotengine.org/download).
- **Python 3.10+** for asset generation scripts.
- **MiniMax API key** (optional, for asset generation) at `~/Madlab/Lockdown/.minimax`.

## Setup

```bash
# Clone
git clone https://github.com/KirkForge/Sword-jin_PWA.git
cd Sword-jin_PWA

# Open in Godot
godot project.godot
```

For headless / CI use (export templates must be installed):
```bash
godot --headless --path . --export-release "HTML5" builds/web/index.html
```

## Export + PWA Deploy

After every HTML5 export, patch the PWA:
```bash
bash scripts/patch_pwa.sh
```

This auto-generates the service worker with correct asset list and cache version.

## Code Style

- 4-space indentation in GDScript
- Signals for decoupling (see existing autoloads)
- snake_case for variables/functions
- Document public API with docstrings (triple-quoted `"""..."""`)
- No emoji in code; keep comments minimal

## Project Structure

```
project.godot         Godot project root
scenes/               .tscn scene files
scripts/              GDScript + Python generators
scripts/autoload/     Global singletons (GameState, PlayFab, etc.)
chapters/             Per-chapter JSON definitions
builds/web/           Export output + PWA files (sw.js, manifest.json, offline.html)
docs/adr/             Architecture decision records
assets/               Generated art, BGM, SFX, voice (gitignored; regenerate)
```

## Git

- Branch from `dev`, PR to `dev` or `main`
- Commit format: `type(scope): message` — see `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Pre-push hooks run via `ci-cleandev`; fix failures, don't bypass

## Testing

Run GUT unit tests headless:
```bash
godot --headless --path . -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit
```

All tests must pass before pushing. Target: 91+ tests, 1276+ assertions.

## Asset Generation

Run individual scripts from `scripts/`:
```bash
python3 scripts/generate_sprites.py
python3 scripts/generate_bgm.py
```

Generated assets land in `assets/art/generated/`, `assets/bgm/`, etc. These are gitignored.

## Deploy

Pushes to `main` trigger GitHub Pages deploy via `.github/workflows/ci.yml` (build + deploy job). The deploy workflow runs the Godot export, patches the PWA, and uploads `builds/web/` to Pages.
