# ADR-002: PWA as the primary deployment target

**Status:** Accepted  
**Date:** 2026-05

## Context

Distributing a mobile game without paying app store fees (30%) or navigating review cycles for content updates.

## Decision

Deploy as a Progressive Web App via HTML5 export + a patched service worker (`scripts/patch_pwa.sh`).

## Rationale

- Install-to-home-screen on Android and iOS without app store
- Offline play via Cache API (full campaign cacheable)
- Instant updates: no review cycle for chapter additions
- One codebase, all platforms

## Consequences

- iOS PWA has limitations (no push notifications, restricted background audio)
- Service worker must be regenerated and cache-busted on each Godot export
- PWA install prompts are browser-dependent; discoverability is worse than app stores
- Future: may wrap in Capacitor or a WebView for store distribution if needed
