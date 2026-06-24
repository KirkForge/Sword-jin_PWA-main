# ADR-001: Godot 4 as the game engine

**Status:** Accepted  
**Date:** 2026-05

## Context

Needed a game engine that exports to HTML5/WASM for PWA deployment, supports GL Compatibility mode for mid-range mobile, and has a permissive license with no runtime royalties.

## Decision

Use Godot 4.4 (GL Compatibility renderer).

## Rationale

- HTML5 export with WASM is first-class in Godot 4
- GL Compatibility mode targets WebGL 2 and mobile GPUs without requiring Vulkan
- MIT license, no royalties
- GDScript is fast to iterate with for solo development
- Unity's 2023 runtime fee incident ruled it out

## Consequences

- No direct Android/iOS native build without Godot's export templates (acceptable; PWA covers the target)
- Godot CI requires the editor binary in GitHub Actions — non-trivial; current CI only lints scripts
- WASM bundle size is larger than a native app; managed by PWA caching
