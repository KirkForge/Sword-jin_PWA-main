#!/usr/bin/env bash
# CI smoke test — run act01_ch001 headlessly and verify completion.
set -euo pipefail

GODOT_BIN="${GODOT_BIN:-godot}"
SCENE="res://scenes/main_with_driver.tscn"
LOG_FILE="${LOG_FILE:-/tmp/godot_smoke.log}"
TIMEOUT_SEC="${TIMEOUT_SEC:-60}"

rm -f ~/.local/share/godot/app_userdata/Swordjin/swordjin_save.json

echo "Running headless smoke test: $SCENE"
timeout "$TIMEOUT_SEC" "$GODOT_BIN" --headless --path . --scene "$SCENE" > "$LOG_FILE" 2>&1 || true

if ! grep -q "Chapter complete" "$LOG_FILE"; then
    echo "FAIL: Chapter did not complete"
    tail -40 "$LOG_FILE"
    exit 1
fi

ERRORS=$(grep -icE 'SCRIPT ERROR|Parse Error|Failed to load script|FATAL|There is no animation' "$LOG_FILE" || true)
if [ "$ERRORS" -gt 0 ]; then
    echo "FAIL: $ERRORS script/runtime errors found"
    grep -iE 'SCRIPT ERROR|Parse Error|Failed to load script|FATAL|There is no animation' "$LOG_FILE" | head -20
    exit 1
fi

echo "PASS: act01_ch001 completed headlessly with no script errors"
