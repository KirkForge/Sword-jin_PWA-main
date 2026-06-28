# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CI: GDScript `--check-only` lint step in workflow
- CI: HTML5 export artifact validation (wasm, pck, js existence checks)
- CI: `patch_pwa.sh` auto-runs after build
- CI: Lighthouse CI audit step (PWA category ≥ 80 threshold)
- Deploy: GitHub Pages workflow via `actions/deploy-pages@v4`
- PWA: `offline.html` branded fallback page for network-off navigation
- PWA: `patch_pwa.sh` auto-generates `ASSETS_TO_CACHE` from actual export artifacts
- PWA: `patch_pwa.sh` auto-computes cache version from `.pck` content hash
- Error: `ErrorScreen` autoloaded CanvasLayer singleton for user-facing error display
- Error: Wired chapter JSON parse failure into error screen
- Error: Wired empty chapter data soft-lock into error screen
- Save: `_migrate_save()` function for forward-compatible save data upgrades
- Save: `_save_indexeddb()` wired into `save_game()` for web IndexedDB persistence
- PlayFab: `_pending_submits` queue persisted to `playfab_state.json` (survives tab close)
- PlayFab: `TITLE_ID` loaded from `ProjectSettings.get_setting("playfab/title_id")` instead of hardcoded literal
- `project.godot`: `[playfab]` settings section with `title_id` key (empty by default)
- `project.godot`: `ErrorScreen` autoload registration
- Docs: `CONTRIBUTING.md` with dev setup guide
- License: MIT `LICENSE` file

### Fixed

- `nightly_dev.sh`: export failure now aborts the pipeline (`exit 1`) instead of silently continuing
- `sw.js`: removed dead push notification listener (no subscription flow implemented)
- `sw.js`: fetch catch handler returns `/offline.html` for navigation requests when uncached
- `sw.js`: updated ASSETS_TO_CACHE to match Godot's `index.*` export naming
- `patch_pwa.sh`: fallback defaults use `index.*` instead of `Swordjin.*`
- `playfab.gd`: `login()` no longer auto-runs when `TITLE_ID` is empty string
- `error_screen.tscn`: fixed missing `parent="."` attributes on child nodes
