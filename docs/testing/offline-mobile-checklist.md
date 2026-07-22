# Offline Mobile PWA Checklist

Manual/semi-automated procedure to verify PWA offline functionality on real mobile devices.

## Prerequisites

- Deployed PWA at the GitHub Pages URL
- Android device with Chrome 114+
- iOS device with Safari 16.4+

## Android Chrome

1. Open the PWA URL in Chrome
2. Tap "Install to Home Screen" when prompted (or via Chrome menu → "Install app")
3. Launch the installed app from home screen
4. Verify: app opens in standalone mode (no browser chrome)
5. Play through act01_ch001 → ch003
6. Verify: game saves persist (check IndexedDB via chrome://inspect → Application → IndexedDB)
7. Enable airplane mode
8. Relaunch the installed app
9. Verify: app boots offline from service worker cache
10. Verify: `index.html`, `.pck`, `.wasm` served from Cache API (check DevTools → Application → Cache Storage)
11. Verify: save made online persists offline (IndexedDB via syncfs)
12. Record: device model, Android version, Chrome version, PASS/FAIL

## iOS Safari

1. Open the PWA URL in Safari
2. Tap Share → "Add to Home Screen"
3. Launch from home screen
4. Verify: app opens in standalone mode (no Safari chrome)
5. Play through act01_ch001 → ch003
6. Verify: game saves persist
7. Enable airplane mode (Control Center)
8. Relaunch the installed app
9. Verify: app boots offline
10. Verify: service worker serves assets from cache
11. Note: `beforeinstallprompt` does not fire on iOS — "Add to Home Screen" is manual
12. Record: device model, iOS version, Safari version, PASS/FAIL

## Results Log

| Date | Device | OS/Browser | Result | Notes |
|------|--------|------------|--------|-------|
| _to be filled on first manual test_ | | | | |

## Failure Escalation

If offline fails on either platform, file as P3 follow-up with:
- Which asset failed to cache (check DevTools → Network → offline filter)
- Whether `sw.js` `ASSETS_TO_CACHE` includes all required files
- Whether `manifest.json` `start_url` is correct