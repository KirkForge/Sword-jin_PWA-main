# ADR-005: PlayFab persistence + pending queue

**Status:** Accepted
**Date:** 2026-07

## Context

The game integrates PlayFab for leaderboard score submission. Players can complete chapters while offline (PWA, no network). Score submissions made before login must not be lost. The PlayFab title ID must be configurable, not hardcoded.

## Decision

- `PlayFab` autoload (`scripts/autoload/playfab.gd`) manages the full lifecycle: auto-login on `_ready()` if title ID is set, queue scores before login, flush queue on login success
- `playfab_state.json` (`user://playfab_state.json`) persists: `custom_id`, `title_id`, `playfab_id`, and `pending_submits` array. Written on first-run (new custom ID) and on every `_save_state()` call. Read on `_load_or_create_custom_id()`. Survives tab close / refresh
- Pending queue flush uses `PENDING_FLUSH_INTERVAL=0.25s` between iterations to avoid bursting the HTTP layer (single HTTPRequest node, serial)
- `login_failed` signal emitted at `playfab.gd:60` (title ID not set) and `playfab.gd:237` (generic error). Consumed by `settings_screen.gd:57-60` for the settings UI toast
- `_migrate_save()` in `game_state.gd:769` handles forward-compatible save data upgrades (version < 2.6 adds missing fields, stamps version to "2.6")

## Code reality

| Claim | Code reality | Match |
|---|---|---|
| PlayFab auto-login | `_ready()` calls `login()` if `TITLE_ID != ""` | Yes |
| Pending queue persisted | `_save_state()` writes to `user://playfab_state.json` | Yes |
| Queue flush rate-limited | 0.25s `PENDING_FLUSH_INTERVAL` between iterations | Yes |
| `login_failed` wired to ErrorScreen | **No** — signal only connects to `settings_screen.gd:57-60` for a toast; no `ErrorScreen.show_error()` call | **Gap** (see Task 3.1) |
| Title ID configurable | `ProjectSettings.get_setting("playfab/title_id", "")` with `set_title_id()` method | Yes |
| `_migrate_save` versioning | Checks `version` field, migrates v < 2.6 → 2.6 with missing fields | Yes |

## Consequences

- Pending scores survive tab close but not IndexedDB clear (playfab_state.json is in `user://` which maps to IndexedDB via syncfs on web)
- `login_failed` is signal-only — the player sees nothing if PlayFab auth fails silently (cloud saves stop syncing with no recourse). This is an open gap, deferred to Task 3.1
- Single HTTPRequest node means all PlayFab calls are serial; a slow leaderboard request blocks score submission
- `_migrate_save` only handles v0 → v2.6; any future schema change requires a new migration step