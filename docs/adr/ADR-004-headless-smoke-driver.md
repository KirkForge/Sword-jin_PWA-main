# ADR-004: Headless smoke driver as integration test

**Status:** Accepted
**Date:** 2026-07

## Context

Need automated verification that all 30 chapters load, transition, and complete without script errors in CI. Unit tests for individual combat math and save migration don't exist yet (see ADR-005). The game must run headless in GitHub Actions (no GPU, no display).

## Decision

Use a headless Godot smoke driver (`scripts/ci/headless_smoke_driver.gd`, 171L) that:
- Instantiates `scenes/main_with_driver.tscn` which autoloads the driver alongside the game
- Each tick (0.2s): finds live enemies in the `"enemy"` group, teleports player onto them, calls `target._die()` directly
- When no enemies remain: sets `GameState.has_gate_key = true`, calls `open_gate()` on the `"gate"` group
- Detects chapter completion via `VictoryScreen.visible` (primary) and `GameState.completed_chapters` growth (fallback for headless environments where VictoryScreen may not render)
- Advances via `ChapterDatabase.set_current_chapter(next_id)` + `ScreenFader.fade_to_black` + `reload_current_scene()`
- Asserts `COMPLETED == 30` and greps for `"All 30 chapters complete"` with zero `SCRIPT ERROR`/`Parse Error`/`FATAL`
- CI step timeout: 6 minutes (`timeout-minutes: 6`)

## Code reality

- Driver file: `scripts/ci/headless_smoke_driver.gd`
- Test harness: `scripts/ci/smoke_test.sh` (shell wrapper, `timeout 300s`)
- CI job: `build` step "Godot headless smoke test" in `.github/workflows/ci.yml`
- Combat is **not** verified — `target._die()` is called directly, damage formulas and HP math are untested
- Victory detection uses `GameState.completed_chapters.size()` as fallback when `VictoryScreen` is unreachable in headless mode

## Consequences

- Catches scene-load regressions, missing node references, chapter-transition crashes, and script parse errors across all 30 chapters
- Does **not** catch combat-balance bugs, damage-formula errors, or `_die()` side-effect failures
- Does **not** verify save/load round-trips or `_migrate_save` correctness
- Motivates unit test coverage (P2.1: GUT tests for combat math + save migration)
- Headless environment lacks textures and display, so any visual-only assertion is unreliable