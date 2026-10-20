#!/usr/bin/env python3
"""
Server and Frontend Endpoints Verification Script
Tests that local HTTP server serves all files with 200 OK,
validates HTML markup, and audits the Arabic RTL compliance.
"""

import http.server
import json
import socketserver
import threading
import time
import urllib.request
from pathlib import Path

PORT = 8085
ROOT_DIR = Path(__file__).resolve().parent.parent


def test_endpoints():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

        def log_message(self, format, *args):
            pass  # Suppress request logging

    httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    print(f"Started test server on http://127.0.0.1:{PORT}")
    time.sleep(1)

    urls = [
        ("/", 200, "Root directory"),
        ("/index.html", 200, "Production HTML"),
        ("/test-harness.html", 200, "Test Harness HTML"),
        ("/css/style.css", 200, "CSS Stylesheet"),
        ("/js/app.js", 200, "JavaScript Engine"),
        ("/data/opportunities.json", 200, "Production Dataset JSON"),
        ("/tests/fixtures/test-opportunities.json", 200, "Test Fixtures Dataset JSON"),
    ]

    all_passed = True
    for path, expected_status, name in urls:
        url = f"http://127.0.0.1:{PORT}{path}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TestProbe/1.0"})
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                body = resp.read()
                if status == expected_status:
                    print(f"  PASS: [{status}] {name} ({path}) - {len(body)} bytes")
                else:
                    print(f"  FAIL: [{status}] {name} ({path}) - Expected {expected_status}")
                    all_passed = False
        except Exception as e:
            print(f"  FAIL: Error fetching {path}: {e}")
            all_passed = False

    # Check index.html content
    with open(ROOT_DIR / "index.html", "r", encoding="utf-8") as f:
        html = f.read()

    print("\nAuditing index.html structure:")
    checks = [
        ('dir="rtl"', 'dir="rtl" present on root'),
        ('lang="ar"', 'lang="ar" present on root'),
        ('meta name="viewport"', 'Responsive mobile viewport meta tag present'),
        ('css/style.css', 'Local stylesheet linked'),
        ('js/app.js', 'Local script linked'),
        ('data-source="data/opportunities.json"', 'Loads production dataset by default'),
        ('id="search-input"', 'Search input present'),
        ('id="filter-category"', 'Category filter select present'),
        ('id="filter-field"', 'Field filter select present'),
        ('id="filter-country"', 'Country filter select present'),
        ('id="filter-status"', 'Deadline status filter select present'),
        ('id="opportunities-grid"', 'Opportunities card grid container present'),
        ('id="empty-state-container"', 'Empty state container present'),
    ]
    for pattern, desc in checks:
        if pattern in html:
            print(f"  PASS: {desc}")
        else:
            print(f"  FAIL: Missing {pattern} - {desc}")
            all_passed = False

    # Check for prohibited CDN links
    prohibited_cdns = ["cdn.", "cdnjs", "unpkg", "jsdelivr", "googleapis", "bootstrapcdn"]
    for cdn in prohibited_cdns:
        if cdn in html:
            print(f"  FAIL: Prohibited external CDN link found: {cdn}")
            all_passed = False

    # Check css/style.css for logical properties and 360px viewport
    with open(ROOT_DIR / "css" / "style.css", "r", encoding="utf-8") as f:
        css = f.read()

    print("\nAuditing css/style.css for logical properties & 360px support:")
    css_checks = [
        ('margin-inline', 'CSS logical margin-inline used'),
        ('padding-inline', 'CSS logical padding-inline used'),
        ('text-align: start', 'CSS logical text-align: start used'),
        ('overflow-x: hidden', 'Zero horizontal scroll overflow guard present'),
        ('min-width: 640px', 'Tablet breakpoint media query present'),
        ('min-width: 1024px', 'Desktop breakpoint media query present'),
        ('--badge-active', 'Active badge custom properties defined'),
        ('--badge-closing', 'Closing soon badge custom properties defined'),
        ('--badge-expired', 'Expired badge custom properties defined'),
    ]
    for pattern, desc in css_checks:
        if pattern in css:
            print(f"  PASS: {desc}")
        else:
            print(f"  FAIL: Missing {pattern} - {desc}")
            all_passed = False

    httpd.shutdown()
    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(test_endpoints())
