# ADR-008: Test coverage expansion strategy with GUT

## Status
Accepted

## Context
Sword-jin PWA had 3.4% test coverage (29 tests, 61 assertions across 8 files) with zero tests for core game systems: level_manager, arena_builder, player movement/skills, enemy AI, and audio.

## Decision
Expand GUT unit tests for core systems using Godot headless mode for deterministic testing. Added 5 new test files covering:
- `test_level_manager.gd` — scene loading, chapter progression, boundaries
- `test_arena_builder.gd` — arena generation, dimensions, spawn positions
- `test_player_movement.gd` — velocity, dodge cooldown, stun, facing
- `test_enemy_ai.gd` — patrol behavior, aggro range, de-aggro, boss phases
- `test_audio_manager.gd` — BGM playback, SFX one-shot, volume control
- `test_error_tracker.gd` — circular buffer, eviction, error reporting

Test count: 29 → 91. Assertion count: 61 → 1276.

## Consequences
- Core game logic is unit-tested with deterministic headless execution
- UI and E2E flows remain untested (need Detox/Maestro for mobile PWA)
- Tests run in CI via GUT headless mode with 5-minute timeout
- New autoloads (WeaponDB, AchievementTracker, etc.) are tested through GameState delegation