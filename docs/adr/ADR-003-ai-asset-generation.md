# ADR-003: AI-generated assets via MiniMax

**Status:** Accepted  
**Date:** 2026-05

## Context

Solo development of 200+ chapter RPG requires large volumes of BGM, SFX, voice clips, and 2D art. Hand-crafting all assets is not feasible at this scale and pace.

## Decision

Generate assets programmatically using MiniMax APIs (music-2.6, T2A, image-01). Generator scripts live in `scripts/generate_*.py`. Generated outputs are committed to `assets/` where file size allows; large binaries (video) are excluded.

## Rationale

- Cost per asset is low vs. commissioning artists or buying packs
- Consistent art style across hundreds of icons is achievable at generation time
- Scripts are reproducible: regenerate at any resolution or with updated prompts
- MiniMax covers music, speech, and image in one vendor relationship

## Consequences

- Asset quality is good-enough, not premium
- API key stored outside repo (`~/Madlab/Lockdown/.minimax`); scripts fail loudly if missing
- Generated art may be inconsistent across batches as models update
- Future: if budget allows, replace placeholder art with commissioned work per act
