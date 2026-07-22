# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- CI: Smoke driver now detects chapter completion via GameState fallback when VictoryScreen is unreachable (fixes 0/30 chapters completed in headless CI)

### Added

- CI: GDScript `--check-only` lint step in workflow
- CI: HTML5 export artifact validation (wasm, pck, js existence checks)
- CI: `patch_pwa.sh` auto-runs after build
- CI: Lighthouse CI audit step (PWA category ≥ 80 threshold)
- CI: `godot --import` step before export (regenerates `.godot/imported/` in fresh CI)
- Deploy: GitHub Pages workflow via `actions/deploy-pages@v4`
- Build: PCK compression via `file_format/compress=true` (Zstandard)
- Build: Removed 78 MB of unused BGM files (only 17 tracks kept)
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
- PWA: `beforeinstallprompt` capture via `html/head_include` inject
- PWA: Install App button on title screen (visible when prompt deferred)
- Save: Periodic autosave every 60s on web platform
- Save: Save on WM_CLOSE_REQUEST (tab close / refresh)
- Save: Improved syncfs error logging in _save_indexeddb
- Docs: `CONTRIBUTING.md` with dev setup guide
- License: MIT `LICENSE` file

### Fixed

- `title_screen.gd`: missing newline before `func _on_daily_challenge_pressed()` causing parse error
- `game_state.gd`: type inference warnings treated as errors (`var ver :=` → `var ver: String =`)
- `game_state.gd`: type inference warnings (`var r :=` → `var r: String =`)
- `ghost_recorder.gd`: type inference warnings (`var data := json.data` → `var data = json.data`)
- `playfab.gd`: type inference warnings (`var TITLE_ID :=` → `var TITLE_ID =`)
- `crit_effect.gd`: removed `class_name CritEffect` (conflicts with autoload singleton)
- `hit_stop.gd`: removed `class_name HitStop` (conflicts with autoload singleton)
- `skeleton_archer.gd`: `attack_damage` not declared (changed to `arrow_damage`)
- `nightly_dev.sh`: export failure now aborts the pipeline (`exit 1`) instead of silently continuing
- `sw.js`: removed dead push notification listener (no subscription flow implemented)
- `sw.js`: fetch catch handler returns `/offline.html` for navigation requests when uncached
- `sw.js`: updated ASSETS_TO_CACHE to match Godot's `index.*` export naming
- `patch_pwa.sh`: fallback defaults use `index.*` instead of `Swordjin.*`
- `playfab.gd`: `login()` no longer auto-runs when `TITLE_ID` is empty string
- `error_screen.tscn`: fixed missing `parent="."` attributes on child nodes
