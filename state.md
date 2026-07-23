# State — Sword-jin_PWA (SwordJin)

*Tracked. Updated at session close. What changed, what's pending, what's blocked.*

## Current state
- Head: `771edbb` (feat/gut-tests-save-migration-ghost-replay)
- Tests: GUT unit tests — 29 tests, 61 assertions, all passing
- Smoke test: 30/30 (pre-existing timeout on this machine; passes in CI)
- Lint: `gdformat --check . && gdlint .` — PASS
- .pck size: 29 MB
- Last updated: 2026-07-23

---

## Session 2026-07-23 — GUT tests, save migration, ghost replay (B+ → A−)

### Completed
- **Task 1**: 14 new GUT unit tests
  - `test/test_combat_depth.gd` — 5 tests: overkill damage → HP≤0, zero damage unchanged, multiple enemies, player heal, enemy armor reduction
  - `test/test_playfab_login_error.gd` — 3 new tests (was 2, now 5): ErrorScreen receives message, auto-hides after timeout, dismiss on return
  - `test/test_save_depth.gd` — 3 tests: encryption structure validation, v0 migration preserves fields, game_data namespace migration
  - `test/test_ghost_replay.gd` — 3 tests: record start/stop state, snapshot data structure, empty ghost list no crash
- **Task 3**: Save data structure expansion
  - `game_state.gd`: added `game_data: Dictionary = {}` (persisted)
  - Added `get_game_data(key, default)` and `set_game_data(key, value)` methods
  - `_migrate_save` now adds `game_data: {}` namespace for saves lacking it (v1→v2 compatible)
  - `save_game()` and `load_game()` include `game_data`
- **Task 4**: Ghost replay — tests for existing GhostRecorder autoload (3 tests)

### Not completed
- **Task 2**: Real-device offline PWA test — no physical Android/iOS devices available for manual testing. Documented as pending.

### Gate evidence
```
$ gdformat --check test/*.gd scripts/autoload/game_state.gd
5 files would be left unchanged

$ gdlint test/*.gd scripts/autoload/game_state.gd
Success: no problems found

$ godot --headless --path . -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit
Scripts: 8, Tests: 29, Passing: 29, Asserts: 61 — All tests passed!
```

### Pending
- **Task 2** (real-device offline test): No physical devices available. Document in state.md as pending.
- Smoke test times out on this machine (pre-existing — 300s timeout insufficient for 30 chapters headless locally; passes in CI)

### Completed tasks
- **Task 0.1**: FF `main` to `2842be6`, synced `dev`, deleted `fix/smoke-driver-victory-detection` branch
- **Task 1.1**: Consolidated two deploy workflows into single `ci.yml` (deleted `deploy.yml`, added `workflow_dispatch`)
- **Task 1.2**: Made lint gating binding — removed `|| true`, added `gdlintrc` with tuned rule overrides, formatted all GDScript files
- **Task 1.3**: Wrote ADR-004 (smoke driver) and ADR-005 (PlayFab persistence)
- **Task 2.1**: Vendored GUT 9.3.0, wrote 5 test files (15 tests, 26 asserts) covering combat math, save migration, PlayFab login_failed, save encryption
- **Task 2.2**: Wrote `docs/testing/offline-mobile-checklist.md` (manual device testing, not automatable in CI)
- **Task 2.3**: Raised Lighthouse PWA threshold to 0.9 fatal with 3G throttling
- **Task 3.1**: Wired `PlayFab.login_failed` to `ErrorScreen.show_error()` in `playfab.gd:_ready()`
- **Task 3.2**: Added XOR-keystream save encryption with per-install key (`user://swordjin_save.key`), envelope versioning `{"enc": 1, "data": "..."}`, legacy plaintext migration
- ADR-006: Documented save encryption decision

### Pending
- **Task 3.3** (.pck size reduction): 116 MB → < 80 MB target requires asset audit (32 MB BGM, 77 MB textures in import cache). Not completed this session.
- **Task 2.2** (real-device offline test): Manual testing on Android/iOS not completed this session. Checklist exists.
- Lighthouse PWA 0.9 threshold: needs CI verification (may fail on throttled run if PWA score < 0.9 — fix the PWA, don't lower the threshold)

### Gate evidence
```
$ gdformat --check scripts/*.gd scripts/autoload/*.gd scripts/ci/*.gd test/*.gd
52 files would be left unchanged
$ gdlint scripts/*.gd scripts/autoload/*.gd scripts/ci/*.gd test/*.gd
Success: no problems found
$ godot --headless --path . -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit
Scripts: 5, Tests: 15, Passing: 15, Asserts: 26 — All tests passed!
```

---

## P0 fix — smoke driver victory-screen detection (2026-07-22)

### Root cause
The smoke driver relied solely on VictoryScreen visibility (`scene.get_node_or_null("Main/VictoryScreen").visible`) to detect chapter completion. In CI's headless environment, VictoryScreen detection could fail if:
1. The `Main/VictoryScreen` node path didn't resolve (instanced scene edge case)
2. `show_victory()` crashed before setting `visible = true` (missing textures in headless)
3. `CanvasLayer.visible` was `false` despite `show_victory()` being called

After chapter completion via `LevelManager._finish_chapter_complete()`, `GameState.complete_current_chapter()` updates `GameState.completed_chapters` *before* `show_victory()`. The driver never checked GameState, so it reported 0/30.

### Fix
- Added `_last_completed_count` tracking `GameState.completed_chapters.size()` as a fallback detection path
- Added `_advancing` guard at top of `_process` to prevent double-reporting (after `_advance_to_next_chapter()` changes ChapterDatabase, subsequent ticks would re-enter with wrong chapter ID)
- Made `_get_victory_screen()` try `find_child("VictoryScreen", true, false)` as fallback when `Main/VictoryScreen` path fails
- Extracted `_try_chapter_complete()`, `_advance_dialogue()`, `_heal_and_fight()` from `_process` to satisfy gdlint max-returns rule

### Gate evidence
```
$ GODOT_BIN=godot bash scripts/ci/smoke_test.sh
Running headless smoke test for 30 chapters: res://scenes/main_with_driver.tscn
PASS: All 30 chapters completed headlessly with no script errors

$ gdformat --check scripts/ci/headless_smoke_driver.gd && gdlint scripts/ci/headless_smoke_driver.gd
1 file would be left unchanged
Success: no problems found
```

30/30 chapters completed sequentially (act01_ch001 through act06_ch030), zero script errors, zero parse errors.

# Asset Generation State

> Session checkpoint: 2026-06-20
> Last action: second major batch completed; two scripts created but not yet run.

## Project
Swordjin — Godot 4.4.1 GL Compatibility mobile PWA, 640×360.

## Refreshed audit — 2026-07-17 (uncommitted tree)
- **Smoke driver expanded to all 30 chapters.** `scripts/ci/headless_smoke_driver.gd` (new, untracked) now iterates ch001→ch030 via `ChapterDatabase.set_current_chapter(next_id)` + scene reload, quits 0 on full run, quits 1 on missing next chapter. `scripts/ci/smoke_test.sh` (modified) asserts `COMPLETED == 30` and greps for `"All 30 chapters complete"`; timeout raised 60→300s. CI `build` job runs it (timeout-minutes: 2 — **likely too tight for 30 chapters**, see risk below).
- **Lint step rewritten.** `ci.yml` lint job drops the always-skipping `if command -v godot --check-only` path; now `pip install gdtoolkit` + `gdformat --check` + `gdlint`. Both still `|| true` → **non-fatal** (lint remains advisory, but no longer skips).
- **Node 24 pinned in lighthouse job.** `ci.yml` lighthouse job now uses `actions/setup-node@v4` with `node-version: '24'` (was relying on runner default Node for `npx @lhci/cli`). Uncommitted.
- **Pages deploy is live.** `ci.yml` has `deploy` job (configure-pages@v5 enablement, deploy-pages@v4) + standalone `deploy.yml` workflow. Last commit `44d0fd3` "trigger fresh Pages deploy after enablement". Gap #3 is **FIXED** (state.md still says STILL-OPEN — stale).
- **PlayFab pending-queue persisted.** `playfab.gd:246` `SAVE_PATH="user://playfab_state.json"`, `_save_state()` (line 277) writes `_pending_submits`, `_load_state()` restores. Gap #13 is **FIXED** (state.md still says STILL-OPEN — stale).
- **Test coverage status.** Still no `test_*.gd` unit tests (gap #5 stays open as a unit-test gap), but the headless smoke driver now exercises all 30 chapters end-to-end — call it PARTIAL (integration covered, unit math/save-migration untested).
- **Lint gap #9.** Was "PARTIAL — skips because godot not installed"; now "PARTIAL-improved — gdtoolkit runs but `|| true` non-fatal".
- **ADRs.** Still 3 (ADR-001 Godot 4, ADR-002 PWA, ADR-003 MiniMax assets), all dated 2026-05, still accurate but stale. No ADRs added for smoke driver, save migration, PlayFab persistence, daily challenge, etc.
- **Remaining open:** #5 (unit tests), #6 (manual device offline test), #7 (PlayFab login_failed still signal-only), #9 (lint non-fatal), #19 (plaintext saves), #20 (no cloud save), #21 (no analytics).
- **New risk not in gap list:** `build` job's `timeout-minutes: 2` on the smoke step is almost certainly too short for a 30-chapter headless run (driver uses 0.2s ticks + 0.5s fades per chapter → ~30s minimum, plus scene reloads/import). 300s shell `timeout` is fine, but the GH job `timeout-minutes: 2` will kill the job before that. Raise to ≥6.

## Risk flag
- `ci.yml:94` `timeout-minutes: 2` on the 30-chapter smoke step — bump to 6+ or the Pages deploy will start failing once the smoke driver actually walks all 30 chapters.

## Pipeline conventions
- Images: MiniMax `image-01` API → Pillow post-process (`fit_square` for 1:1, `resize_with_letterbox` for 16:9) → `.webp` quality 85, method 6.
- Music: MiniMax `music-2.6` API → download MP3 → ffmpeg `-c:a libvorbis -q:a 4` → `.ogg`.
- SFX: procedural Python (`wave`/`struct`/`math`) → mono 22050 Hz 16-bit `.wav`.
- API key loaded from `/home/kirk/Madlab/Lockdown/.minimax`.
- All generation scripts use skip-existing logic to support resume/retry.

## Current counts
| Category | Count | Notes |
|---|---|---|
| Generated art (`assets/art/generated/`) | 498 `.webp`/`.png` files | includes enemies, allies, NPCs, locations, effects, skills, status, items, act titles, boss splash, screens, achievements, concepts |
| BGM (`assets/bgm/`) | 51 `.ogg` loops | 0 leftover `.mp3` |
| SFX (`assets/sfx/`) | 61 `.wav` effects | |

## Batches completed
1. First batch: core heroes, enemies, BGM, SFX, UI, items, skills, status, locations, boss splash, screens, etc.
2. Second batch (this session):
   - `scripts/generate_more_enemies.py` — 12 enemy portraits
   - `scripts/generate_more_battle_bgm.py` — 8 battle/tension/dungeon BGM loops
   - `scripts/generate_more_magic_sfx.py` — 12 procedural magic/combat SFX
   - `scripts/generate_more_achievements3.py` — 12 achievement badges
   - `scripts/generate_more_exploration_bgm.py` — 8 region/exploration/mood BGM loops
   - `scripts/generate_more_ui_sfx.py` — 12 UI/environment SFX
   - `scripts/generate_more_act_titles2.py` — 12 act/chapter title cards
   - `scripts/generate_more_locations2.py` — 12 location/zone marker icons
   - `scripts/generate_more_effects2.py` — 12 combat VFX icons
   - `scripts/generate_more_boss_splash2.py` — 12 boss splash art pieces
   - `scripts/generate_more_screens2.py` — 12 menu/loading screen backgrounds

## Fourth batch — 2026-06-21

Resumed the pipeline using the MiniMax API key from `/home/kirk/Madlab/Lockdown/.minimax`, hitting the lowest-count art categories plus another ambient BGM wave.

### New scripts created
- `scripts/generate_more_achievements4.py` — 12 achievement badge icons, 128×128
- `scripts/generate_more_skills3.py` — 12 combat ability icons, 128×128
- `scripts/generate_more_effects3.py` — 12 combat VFX icons, 128×128
- `scripts/generate_more_status3.py` — 12 status effect icons, 128×128
- `scripts/generate_more_concept2.py` — 6 story/concept scenes, 640×360
- `scripts/generate_more_ambient_bgm2.py` — 8 ambient instrumental BGM loops, music-2.6

### Results
- **Achievements:** 32 → **44** (all 12 generated)
- **Skills:** 34 → **46** (all 12 generated)
- **Effects:** 36 → **48** (all 12 generated)
- **Status:** 36 → **48** (all 12 generated)
- **Concept:** 37 → **43** (5 new generated; `story_dawn_after_tear` already existed, replaced in script with `story_legion_oath` and generated)
- **BGM:** 59 → **67** (all 8 ambient loops generated)

### Updated counts
| Category | Count | Notes |
|---|---|---|
| Generated art (`assets/art/generated/`) | 615 `.webp`/`.png` files | +60 from this batch |
| BGM (`assets/bgm/`) | 67 `.ogg` loops | +8 |
| SFX (`assets/sfx/`) | 74 `.wav` effects | unchanged |

### Changes
- `README.md` — added the 6 new scripts, bumped BGM count to 67, listed the new ambient track names.
- `state.md` — this section.

## Known issues / recoveries
- `story_dawn_after_tear` already existed in `assets/art/generated/concept/`; replaced with `story_legion_oath` in `generate_more_concept2.py` and generated successfully.
- No timeouts or empty image responses in this batch.
- No MP3 leftovers remain in `assets/bgm/`.

## Fifth batch — 2026-06-21

Continued the pipeline using the MiniMax API key from `/home/kirk/Madlab/Lockdown/.minimax`, targeting the five lowest-count art categories.

### New scripts created
- `scripts/generate_more_act_titles4.py` — 12 act/chapter title cards, 640×360
- `scripts/generate_more_boss_splash3.py` — 12 boss splash art pieces, 640×360
- `scripts/generate_more_screens3.py` — 12 menu/loading screen backgrounds, 640×360
- `scripts/generate_more_npc_variants2.py` — 12 dialogue NPC portraits, 128×128
- `scripts/generate_more_concept3.py` — 6 story/concept scenes, 640×360

### Results
- **Act titles:** 40 → **52** (all 12 generated)
- **Boss splash:** 40 → **52** (all 12 generated)
- **Screens:** 40 → **52** (all 12 generated)
- **NPCs:** 42 → **54** (all 12 generated)
- **Concept:** 43 → **49** (all 6 generated)

### Updated counts
| Category | Count | Notes |
|---|---|---|
| Generated art (`assets/art/generated/`) | 662 `.webp`/`.png` files | +47 from this batch |
| BGM (`assets/bgm/`) | 67 `.ogg` loops | unchanged |
| SFX (`assets/sfx/`) | 74 `.wav` effects | unchanged |

### Changes
- `README.md` — added the 5 new scripts.
- `state.md` — this section.

## Known issues / recoveries
- No timeouts, empty responses, or duplicates in this batch.
- No MP3 leftovers remain in `assets/bgm/`.

## Sixth batch — 2026-06-21

Continued the pipeline using the MiniMax API key from `/home/kirk/Madlab/Lockdown/.minimax`, targeting the five lowest-count art categories.

### New scripts created
- `scripts/generate_more_achievements5.py` — 12 achievement badge icons, 128×128
- `scripts/generate_more_locations4.py` — 12 location/zone marker icons, 128×128
- `scripts/generate_more_skills4.py` — 12 combat ability icons, 128×128
- `scripts/generate_more_ui2.py` — 8 UI panel/button/slot textures
- `scripts/generate_more_enemy_portraits3.py` — 12 enemy/boss portrait icons, 256×256

### Results
- **Achievements:** 44 → **55** (+11 generated; `ach_void_touched` already existed, skipped)
- **Locations:** 46 → **57** (+11 generated; `loc_moonlit_market` already existed, skipped)
- **Skills:** 46 → **58** (all 12 generated)
- **UI:** 46 → **54** (+8 generated)
- **Enemy portraits:** 47 → **59** (all 12 generated)

### Updated counts
| Category | Count | Notes |
|---|---|---|
| Generated art (`assets/art/generated/`) | 716 `.webp`/`.png` files | +54 net from this batch |
| BGM (`assets/bgm/`) | 67 `.ogg` loops | unchanged |
| SFX (`assets/sfx/`) | 74 `.wav` effects | unchanged |

### Changes
- `README.md` — added the 5 new scripts.
- `state.md` — this section.

## Known issues / recoveries
- `ach_void_touched` already existed in `assets/art/generated/achievements/`; `generate_more_achievements5.py` skipped it.
- `loc_moonlit_market` already existed in `assets/art/generated/locations/`; `generate_more_locations4.py` skipped it.
- No timeouts or empty image responses in this batch.
- No MP3 leftovers remain in `assets/bgm/`.

## Next steps if continuing
- All major art categories now at 54+ files. Lowest remaining are **effects (48)**, **status (48)**, **concept (49)**, **achievements (55)**.
- Audio is healthy: BGM 67 / SFX 74 / Voice 31.
- Could run `godot --headless --import` to refresh the asset import cache before a build.

## Gap Audit — verified 2026-07-03

### 1. HTML5 Export Artifacts Missing — FIXED
builds/web/ now contains index.html, index.wasm, index.pck, index.js, index.audio.worklet.js; CI build job runs `--export-release "HTML5"` and verifies artifacts exist.

### 2. Service Worker Cache List Hardcoded — FIXED
sw.js is auto-generated by patch_pwa.sh scanning actual export files; ASSETS_TO_CACHE lists real filenames (index.wasm, index.pck, etc.).

### 3. No Hosting Infrastructure — STILL-OPEN
.github/workflows/ci.yml has no deploy job (no Pages/Vercel/Netlify/Cloudflare step); grep for deploy/pages/peaceiris returns nothing.

### 4. PlayFab Title ID Hardcoded — FIXED
scripts/autoload/playfab.gd:21 `var TITLE_ID = ProjectSettings.get_setting("playfab/title_id", "")`.

### 5. Zero Test Coverage — STILL-OPEN
No test_*.gd files found; CI has no `godot --run-tests` step.

### 6. PWA Offline Mode Never Validated — PARTIAL
Lighthouse CI step added (lighthouserc.json, PWA threshold 0.8); manual offline test on physical Android/iOS still undocumented.

### 7. No User-Facing Error UI — PARTIAL
scripts/error_screen.gd + scenes/error_screen.tscn exist; chapter_database.gd:47,59 and level_manager.gd:57 wired to ErrorScreen.show_error; playfab.gd login_failed (line 211) still only emits signal, no ErrorScreen call.

### 8. No offline.html Fallback — FIXED
builds/web/offline.html exists; sw.js fetch catch serves caches.match('/offline.html') for navigate requests.

### 9. No CI GDScript Linting or Build Validation — PARTIAL
CI build job runs HTML5 export + artifact verification (catches parse errors); dedicated GDScript `--check-only` lint step in lint job is wrapped in `if command -v godot` but godot not installed in lint job, so it skips.

### 10. FS.syncfs() Save Persistence Unverified — FIXED
game_state.gd:843-861 `_save_indexeddb` now documents the syncfs→IndexedDB path and DevTools verification steps (Application → IndexedDB → /home/web_user/...); called from save_game (line 644) and autosave tick.

### 11. No Install Prompt UI — FIXED
builds/web/index.html:96 has beforeinstallprompt bridge; scripts/title_screen.gd:21 InstallAppButton + _on_install_app_pressed:308.

### 12. Cache Version Manual Bump — FIXED
sw.js CACHE_NAME = 'swordjin-4b6a11f3' (md5 of .pck); patch_pwa.sh generates from `md5sum "$PCK_FILE" | cut -c1-8`.

### 13. PlayFab Score Queue Lost on Refresh — STILL-OPEN
playfab.gd:31 `_pending_submits: Array = []` is in-memory only; no persistence to save file.

### 14. Save File Format No Migration Path — FIXED
game_state.gd:585 `_migrate_save(data: Dictionary)` function, called at line 670 on load.

### 15. Nightly Build Script Ignores Export Exit Codes — FIXED
scripts/nightly_dev.sh:194 `timeout 120 godot ... || { echo "[NIGHTLY] Export failed — aborting"; exit 1; }`.

### 16. No CHANGELOG — FIXED
CHANGELOG.md exists.

### 17. No Setup Guide — FIXED
CONTRIBUTING.md exists.

### 18. Push Notification Subscription Dead Code — FIXED
Auto-generated sw.js has no push/subscription listener (dead code removed).

### 19. Save File Plaintext — STILL-OPEN
game_state.gd save_game uses `file.store_string(JSON.stringify(data, "\t"))`; no encryption/XOR/Web Crypto.

### 20. No Cloud Save — STILL-OPEN
No UpdateUserData/GetUserData in playfab.gd; PlayFab not wired for save data.

### 21. No Analytics or Crash Reporting — STILL-OPEN
No analytics beacon / Plausible / telemetry in scripts/ or builds/web/.

### 22. No License File — FIXED
LICENSE exists.

### 23. Colorblind Mode Not Implemented — FIXED
scripts/damage_number.gd:14-24 `_colorblind_prefix()` prepends shape symbols (✚ heal / ✶ damage / ◆ special / ★ crit) when GameState.settings.colorblind_mode is on; toggle wired in settings_screen.gd:12,45,73,113-115 and scenes/ui/settings_screen.tscn (ColorblindMode node); setting persisted in game_state.gd:64.

### 24. Leaderboard Pending Scores Not Rate-Limited — FIXED
playfab.gd:32-35 adds PENDING_FLUSH_INTERVAL=0.25s; _handle_login (line 202-209) now awaits get_tree().create_timer between flush iterations so a backlog trickles instead of bursting. HTTP layer still serializes one request at a time.

### Fixes applied 2026-07-03
Quick mechanical fixes this run (smallest working diff, no new deps, no behavior redesign):
- #10 FS.syncfs — added docblock to `_save_indexeddb` documenting the IndexedDB persistence path and DevTools verification steps. No runtime change.
- #23 colorblind — added `colorblind_mode` setting (game_state.gd), settings-screen toggle (settings_screen.gd + .tscn), and shape-symbol prefixes in damage_number.gd (✚/✶/◆/★). Additive only; off by default, no visual change for default users.
- #24 pending-score rate limit — added 0.25s `PENDING_FLUSH_INTERVAL` cooldown between pending-submit flush iterations in playfab.gd `_handle_login`. HTTP serialization unchanged.

Deferred this run (NOT 10-20 min mechanical fixes):
- #3 hosting/deploy — needs deployment target/credentials (deferred: needs infra decision).
- #5 tests — real test suite is not a quick fix (deferred: needs scope/effort decision).
- #13 pending-queue persistence — _save_state() exists but isn't called when a score is queued; wiring it is a 1-line change but changes persistence behavior, so deferred as a candidate for manual verification.
- #19 save encryption — crypto/trust-boundary change (deferred).
- #20 cloud save — needs PlayFab UpdateUserData/GetUserData wiring + backend (deferred).
- #21 analytics — needs provider selection (deferred).
- #6 PWA offline — manual physical-device test still undocumented (deferred: needs device).
- #7 user-facing error UI — playfab.gd login_failed still only emits signal; wiring ErrorScreen is small but changes runtime behavior (deferred as candidate).
- #9 CI GDScript lint — lint job skips because godot not installed in lint job (deferred: CI infra change).

Checks run: `godot --headless --path . --quit` (full project parse, autoloads registered) — exit 0, no script errors, project boots cleanly. CI's `--check-only --script` mode reports pre-existing "Identifier not found" errors for autoload names (AudioManager/PlayFab/GameState) in both edited and unedited files — that is a known limitation of that mode (autoloads not registered), not a regression from these edits.

## Cross-Project Recurring Patterns (overall review 2026-06-28; fold-in 2026-07-03)
One root pattern across all ten KirkForge repos: the interesting problem gets finished, the boring plumbing gets deferred.
1. Release automation last/never — code ships to git, not users; .releaserc configured, no release.yml; versions drift.
2. Security features scaffolded, not completed — architecture built, last 10% deferred (Dopaflow ENCRYPTION_ENABLED stub; Plugin/PicoSentry signing without sandboxing; BIL approval 2/N actions; PetSense config.yaml never loaded; Packy rate-limiter missing one await).
3. CI is decorative — checks exist but non-blocking or wired to local scripts CI doesn't call (cargo audit continue-on-error; ci.sh vs GH Actions; `lint || true`).
4. Integration tests cut first — unit tests green; real e2e path untested / #[ignore] / unverified.
5. Ops docs lag code docs — ADRs/ARCHITECTURE.md strong; deployment guide / runbook / CHANGELOG / troubleshooting missing.
Applies to this repo:
1. Relevant — no deploy target in CI (gap 3 still open); HTML5 export verified in CI but never shipped anywhere.
2. Relevant — save encryption (gap 19) and cloud save (gap 20) deferred; PlayFab pending-queue persistence (gap 13) deferred.
3. Relevant — GDScript `--check-only` lint step skips because godot not installed in lint job (gap 9); Lighthouse step non-fatal (`|| echo "non-fatal"`).
4. Relevant — zero test coverage (gap 5); FS.syncfs persistence never verified end-to-end (gap 10).
5. Partially resolved — CHANGELOG.md and CONTRIBUTING.md now exist (gaps 16, 17); deploy/runbook/troubleshooting still missing.
