# ADR-009: Lighthouse mobile preset for PWA

## Status
Accepted

## Context
Sword-jin PWA is a mobile-first action RPG deployed as a PWA. The Lighthouse CI was configured with `preset: "desktop"`, testing desktop performance metrics for a game designed for mobile devices. No accessibility testing was included.

## Decision
Switch Lighthouse CI configuration to:
- `preset: "mobile"` with simulated 3G throttling
- `numberOfRuns: 3` for statistical stability
- Added accessibility category alongside performance and PWA
- Performance threshold: ≥ 0.5 (error threshold, mobile is harder)
- Accessibility threshold: ≥ 0.7 (warning threshold)
- PWA threshold: ≥ 0.9 (error threshold, maintained from before)

## Consequences
- CI catches mobile-specific performance regressions (3G throttling, CPU slowdown)
- Accessibility warnings surface for keyboard navigation, ARIA labels, contrast
- Performance score may be lower on mobile preset — 0.5 threshold accounts for this
- 3 runs per CI adds ~30 seconds to lighthouse job