# ADR-007: game_state.gd decomposition into subsystem autoloads

## Status
Accepted

## Context
`game_state.gd` was a 1953-line god object containing save/load, encryption, weapons, achievements, daily challenges, streaks, rested XP, settings, inventory, bestiary, and loot systems. Adding a feature required navigating 2000 lines, making the codebase difficult to test and maintain.

## Decision
Decompose `game_state.gd` into focused autoload singletons:
- **SaveManager** (76 lines) — encryption, save migration, key management
- **WeaponDB** (204 lines) — weapon/skill data, rarity, loot rolling, collection progress
- **AchievementTracker** (309 lines) — achievement badges, progress, condition checking
- **DailyChallengeManager** (145 lines) — daily challenge generation and completion
- **SettingsManager** (35 lines) — audio, display, accessibility settings
- **BestiaryManager** (241 lines) — enemy kill tracking and bestiary data
- **StreakManager** (178 lines) — daily login streaks, rested XP, date validation

`game_state.gd` retains core state variables and delegation methods for backward compatibility. External callers can use either `GameState.method()` or `Subsystem.method()` directly.

## Consequences
- Each subsystem is independently testable
- `game_state.gd` reduced from 1953 → ~814 lines (as coordinator)
- All 91 tests pass after decomposition
- Autoload registration order matters (subsystems must come after GameState in project.godot)
- Delegation methods add slight overhead but maintain backward compatibility