#!/usr/bin/env python3
"""Browser PWA smoke test for Swordjin.

Serves builds/web locally, loads it in headless Chromium, and verifies the
canvas appears and no fatal errors are emitted. Godot Web warnings such as
missing BGM or platform limitations are ignored.
"""
import http.server
import socketserver
import threading
import time
import sys
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

BUILD_DIR = Path(__file__).resolve().parent.parent.parent / "builds" / "web"
IGNORED_PATTERNS = [
    re.compile(r"WARNING: .*"),
    re.compile(r"Failed to load BGM"),
    re.compile(r"BGM not found"),
    re.compile(r"OS::get_unique_id"),
    re.compile(r"No interface 'godot' registered"),
    re.compile(r"push_warning"),
    re.compile(r"platform/web"),
]

def is_ignored(message: str) -> bool:
    return any(p.search(message) for p in IGNORED_PATTERNS)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUILD_DIR), **kwargs)
    def log_message(self, format, *args):
        pass

with socketserver.TCPServer(("127.0.0.1", 0), Handler) as httpd:
    httpd.allow_reuse_address = True
    port = httpd.server_address[1]
    url = f"http://127.0.0.1:{port}/index.html"
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(1)

    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.on("pageerror", lambda exc: errors.append(f"PAGE ERROR: {exc}"))
        page.on("console", lambda msg: (
            errors.append(f"CONSOLE {msg.type}: {msg.text}")
            if msg.type in ("error",) and not is_ignored(msg.text)
            else None
        ))
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("canvas", timeout=20000)
        time.sleep(4)
        title = page.title()
        canvas_present = page.locator("canvas").count() > 0
        print(f"Page title: {title}")
        print(f"Canvas present: {canvas_present}")
        if not canvas_present:
            errors.append("Godot canvas did not appear")
        page.screenshot(path="/tmp/swordjin_pwa.png")
        browser.close()

    httpd.shutdown()

if errors:
    print("Browser errors:")
    for e in errors:
        print(e)
    sys.exit(1)
print("PASS: PWA loaded in browser with no fatal errors")
