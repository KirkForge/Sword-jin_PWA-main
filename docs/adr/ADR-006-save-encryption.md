# ADR-006: Save encryption at rest

**Status:** Accepted
**Date:** 2026-07

## Context

Player saves are stored in IndexedDB (via syncfs) as plaintext JSON (`user://swordjin_save.json`). On a shared device, saves are trivially inspectable and editable. If PlayFab cloud save ships, the local cache should be encrypted before any sync so a compromised cloud store can't serve a tampered save back to the player.

## Decision

Add a XOR-keystream encryption layer around `save_game()`/`load_game()`:

- **Key management**: A 256-bit random key is generated on first run (`user://swordjin_save.key`) using `Crypto.generate_random_bytes(32)`. The key is stored locally and never leaves the device.
- **Encryption**: On save, `JSON.stringify(data)` is XOR-encrypted with the per-install key and base64-encoded into an envelope `{"enc": 1, "data": "<base64>"}`.
- **Decryption**: On load, if the file contains the `enc` envelope, it decrypts; if it contains plaintext JSON (legacy save), it passes through for migration via `_migrate_save()`.
- **Version**: `enc: 1` in the envelope allows future encryption scheme upgrades without breaking existing saves.

## Code reality

- `_encrypt()` and `_decrypt()` in `game_state.gd` implement the XOR-keystream + base64 envelope.
- `_get_save_key()` generates or loads the per-install key.
- `save_game()` writes encrypted data; `load_game()` decrypts transparently.
- `_migrate_save()` still handles schema version migration (v0 → v2.6) after decryption.

## Consequences

- Casual save tampering (opening the JSON in a text editor) is blocked; the save appears as base64 ciphertext.
- A determined attacker with access to the key file can still decrypt; this matches the threat model (casual tampering, not a determined attacker with reverse-engineering skills).
- Legacy plaintext saves migrate transparently — `_decrypt()` passes through non-envelope JSON.
- Key loss (clearing `user://swordjin_save.key`) makes the save unreadable. This is documented honestly: the key is stored alongside the save, so the threat model is "opportunistic tampering," not "targeted attack."
- No external crypto dependencies; uses Godot built-in `Crypto` for key generation and `Marshalls` for base64.