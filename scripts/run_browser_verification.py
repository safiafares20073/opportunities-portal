#!/usr/bin/env python3
"""
Real-Browser Verification Script for Opportunities Portal
==========================================================
Uses installed Google Chrome / Microsoft Edge via Chromium DevTools Protocol (CDP)
to test the actual running application in a real browser engine:
1. Loads test-harness.html and index.html over local HTTP server.
2. Interacts with search, category filters, and status filters.
3. Verifies deadline badges ("متاحة", "تغلق قريبًا", "منتهية").
4. Tests empty state behavior.
5. Verifies document.documentElement.scrollWidth <= window.innerWidth at 360px.
6. Captures genuine PNG screenshots directly from the browser rendering engine.
"""

import base64
import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

# Try to import websocket from websocket-client
try:
    import websocket
except ImportError:
    print("[ERROR] websocket-client library not available.")
    sys.exit(1)

HTTP_PORT = 8095
CDP_PORT = 9255
ROOT_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_DIR = Path(os.environ.get("GEMINI_ARTIFACT_DIR", r"C:\Users\DELL\.gemini\antigravity\brain\a8f26efd-4c7c-4159-bd88-d5b8d0129f21"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# Locate Chrome or Edge
CHROME_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

def find_browser():
    for p in CHROME_PATHS:
        if p.exists():
            return str(p)
    raise RuntimeError("No supported Chromium browser found (Chrome/Edge).")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


def start_http_server(port=HTTP_PORT):
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    return httpd



class CDPClient:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=15)
        self.msg_id = 0

    def send(self, method, params=None):
        self.msg_id += 1
        payload = {"id": self.msg_id, "method": method, "params": params or {}}
        self.ws.send(json.dumps(payload))
        while True:
            raw = self.ws.recv()
            data = json.loads(raw)
            if data.get("id") == self.msg_id:
                if "error" in data:
                    raise RuntimeError(f"CDP Error ({method}): {data['error']}")
                return data.get("result", {})

    def evaluate(self, expression):
        res = self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        result_obj = res.get("result", {})
        if "value" in result_obj:
            return result_obj["value"]
        return result_obj

    def capture_screenshot(self, output_path: Path):
        res = self.send("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(res["data"])
        with open(output_path, "wb") as f:
            f.write(data)
        print(f"  [SAVED SCREENSHOT] -> {output_path.name} ({len(data)} bytes)")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def run_360_viewport_check(browser_bin, http_port):
    temp_p = tempfile.mkdtemp(prefix="chrome_360_check_")
    cmd = [
        browser_bin,
        "--headless=new",
        "--remote-debugging-port=9227",
        "--remote-allow-origins=*",
        "--window-size=360,740",
        f"--user-data-dir={temp_p}",
        f"http://127.0.0.1:{http_port}/test-harness.html"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9227/json", timeout=5)
        targets = json.loads(req.read().decode())
        page_t = next(x for x in targets if x['type'] == 'page')
        c = CDPClient(page_t['webSocketDebuggerUrl'])
        c.send("Page.enable")
        c.send("Runtime.enable")
        time.sleep(1.5)
        metrics = c.evaluate("""
            (() => {
                const prevHtml = document.documentElement.style.overflowX;
                const prevBody = document.body.style.overflowX;
                document.documentElement.style.overflowX = 'visible';
                document.body.style.overflowX = 'visible';

                const innerW = window.innerWidth;
                const scrollW = document.documentElement.scrollWidth;
                const bodyScrollW = document.body.scrollWidth;

                document.documentElement.style.overflowX = prevHtml;
                document.body.style.overflowX = prevBody;

                return {
                    innerW: innerW,
                    scrollW: scrollW,
                    bodyScrollW: bodyScrollW,
                    noOverflow: scrollW <= innerW && bodyScrollW <= innerW
                };
            })()
        """)
        c.capture_screenshot(ARTIFACT_DIR / "real_browser_test_harness_360px.png")
        c.close()
        return metrics
    finally:
        p.terminate()
        try:
            p.wait(timeout=2)
        except Exception:
            pass
        shutil.rmtree(temp_p, ignore_errors=True)



def run_browser_tests():
    print("=" * 70)
    print("Opportunities Portal — Real Browser End-to-End Verification")
    print("=" * 70)

    browser_bin = find_browser()
    print(f"Browser Binary: {browser_bin}")
    print(f"Artifact Dir  : {ARTIFACT_DIR}")

    # Start HTTP server
    httpd = start_http_server()
    print(f"Local HTTP Server: http://127.0.0.1:{HTTP_PORT}")
    time.sleep(1)

    temp_profile = tempfile.mkdtemp(prefix="chrome_test_profile_")

    chrome_cmd = [
        browser_bin,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={temp_profile}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"http://127.0.0.1:{HTTP_PORT}/test-harness.html"
    ]

    print("Launching Chromium in headless mode with remote debugging...")
    proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    test_results = {}
    cdp = None

    try:
        # Get target websocket URL
        list_url = f"http://127.0.0.1:{CDP_PORT}/json"
        req = urllib.request.urlopen(list_url, timeout=5)
        targets = json.loads(req.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]
        print(f"Connected to CDP session: {ws_url[:50]}...")

        cdp = CDPClient(ws_url)
        cdp.send("Page.enable")
        cdp.send("Runtime.enable")
        cdp.send("DOM.enable")
        cdp.send("Emulation.setDeviceMetricsOverride", {
            "width": 1280,
            "height": 800,
            "deviceScaleFactor": 1,
            "mobile": False
        })

        time.sleep(2)  # Wait for page data to load via fetch

        # --- TEST 1: Initial Load & Test Fixtures Count ---
        print("\n[Test 1] Initial Load of test-harness.html:")
        card_count = cdp.evaluate("document.querySelectorAll('.opportunity-card').length")
        results_text = cdp.evaluate("document.getElementById('results-count').textContent.trim()")
        test_banner = cdp.evaluate("document.querySelector('.test-env-banner') !== null")
        print(f"  * Cards rendered: {card_count} (Expected: 8)")
        print(f"  * Results text : '{results_text}'")
        print(f"  * Test banner present: {test_banner}")
        test_results["Test 1: Initial Load (8 cards)"] = (card_count == 8 and test_banner)
        cdp.capture_screenshot(ARTIFACT_DIR / "real_browser_test_harness_desktop.png")

        # --- TEST 2: Deadline Status Badges ---
        print("\n[Test 2] Arabic Deadline Status Badges Verification:")
        badges = cdp.evaluate("""
            (() => {
                const badges = Array.from(document.querySelectorAll('.status-badge'));
                return {
                    total: badges.length,
                    active: badges.filter(b => b.classList.contains('status-active')).length,
                    closing: badges.filter(b => b.classList.contains('status-closing')).length,
                    expired: badges.filter(b => b.classList.contains('status-expired')).length,
                    texts: badges.map(b => b.textContent.trim())
                };
            })()
        """)
        print(f"  * Total Badges: {badges['total']}")
        print(f"  * 'متاحة' (Active): {badges['active']}")
        print(f"  * 'تغلق قريبًا' (Closing soon): {badges['closing']}")
        print(f"  * 'منتهية' (Expired): {badges['expired']}")
        test_results["Test 2: Deadline Badges (متاحة/تغلق قريبًا/منتهية)"] = (
            badges["active"] >= 4 and badges["closing"] >= 2 and badges["expired"] >= 1
        )

        # --- TEST 3: Real-Time Keyword Search ---
        print("\n[Test 3] Interactive Search via UI Interaction:")
        cdp.evaluate("""
            (() => {
                const input = document.getElementById('search-input');
                input.value = 'الذكاء الاصطناعي';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            })()
        """)
        time.sleep(0.5)
        search_count = cdp.evaluate("document.querySelectorAll('.opportunity-card').length")
        search_results_text = cdp.evaluate("document.getElementById('results-count').textContent.trim()")
        print(f"  * Query: 'الذكاء الاصطناعي'")
        print(f"  * Matched Cards: {search_count}")
        print(f"  * Results Text: '{search_results_text}'")
        test_results["Test 3: Interactive Keyword Search"] = (search_count >= 1)
        cdp.capture_screenshot(ARTIFACT_DIR / "real_browser_search_filtered.png")

        # Reset search
        cdp.evaluate("document.getElementById('reset-filters-btn').click()")
        time.sleep(0.5)

        # --- TEST 4: Combined Filter UI Interaction ---
        print("\n[Test 4] Combined Filter Interaction (Category + Status):")
        cdp.evaluate("""
            (() => {
                const cat = document.getElementById('filter-category');
                cat.value = 'Scholarship';
                cat.dispatchEvent(new Event('change', { bubbles: true }));

                const status = document.getElementById('filter-status');
                status.value = 'متاحة';
                status.dispatchEvent(new Event('change', { bubbles: true }));
            })()
        """)
        time.sleep(0.5)
        combo_count = cdp.evaluate("document.querySelectorAll('.opportunity-card').length")
        combo_text = cdp.evaluate("document.getElementById('results-count').textContent.trim()")
        print(f"  * Category='Scholarship' + Status='متاحة'")
        print(f"  * Filtered Cards: {combo_count}")
        print(f"  * Results Text: '{combo_text}'")
        test_results["Test 4: Combined Dropdown Filters"] = (combo_count == 2)

        # --- TEST 5: Actionable Empty State ---
        print("\n[Test 5] Empty State Trigger & Reset Interaction:")
        cdp.evaluate("""
            (() => {
                const input = document.getElementById('search-input');
                input.value = 'كلمة_بحث_مستحيلة_الوجود_999';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            })()
        """)
        time.sleep(0.5)
        empty_card_count = cdp.evaluate("document.querySelectorAll('.opportunity-card').length")
        empty_title = cdp.evaluate("""
            (() => {
                const el = document.querySelector('.empty-state-title');
                return el ? el.textContent.trim() : null;
            })()
        """)
        reset_visible = cdp.evaluate("document.getElementById('empty-state-reset-btn') !== null")
        print(f"  * Cards visible: {empty_card_count} (Expected: 0)")
        print(f"  * Empty Title  : '{empty_title}'")
        print(f"  * Reset button : {reset_visible}")
        test_results["Test 5: Empty State Trigger"] = (empty_card_count == 0 and "لم يتم العثور" in (empty_title or ""))
        cdp.capture_screenshot(ARTIFACT_DIR / "real_browser_empty_state.png")

        # Reset via empty state button
        cdp.evaluate("document.getElementById('empty-state-reset-btn').click()")
        time.sleep(0.5)

        # --- TEST 6: Strict 360px Viewport Overflow Verification ---
        # IMPORTANT: We launch a SEPARATE Chrome process for this test.
        # Setting setDeviceMetricsOverride(360) after setDeviceMetricsOverride(1280)
        # in the same CDP session causes Chrome headless to return innerWidth=440 on
        # this machine (a known Chrome headless quirk on Windows).
        # By starting a fresh process and applying 360px as the very first override
        # (before navigating to any real page), we get innerWidth=360 reliably.
        print("\n[Test 6] Strict 360px Mobile Viewport & ScrollWidth Verification:")
        print("  (using isolated Chrome process to guarantee clean 360px state)")
        metrics = None
        temp_360_profile = tempfile.mkdtemp(prefix="chrome_360_strict_")
        import socket as _socket
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as _s:
            _s.bind(('127.0.0.1', 0))
            cdp_360_port = _s.getsockname()[1]

        proc_360 = subprocess.Popen([
            browser_bin,
            "--headless=new",
            f"--remote-debugging-port={cdp_360_port}",
            "--remote-allow-origins=*",
            "--disable-gpu",
            f"--user-data-dir={temp_360_profile}",
            "about:blank"   # ← critical: no real page yet; override goes first
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        cdp_360 = None
        try:
            req_360 = urllib.request.urlopen(
                f"http://127.0.0.1:{cdp_360_port}/json", timeout=5)
            targets_360 = json.loads(req_360.read().decode())
            page_360 = next(x for x in targets_360 if x.get("type") == "page")
            cdp_360 = CDPClient(page_360["webSocketDebuggerUrl"])
            cdp_360.send("Page.enable")
            cdp_360.send("Runtime.enable")
            # Step 1: Set 360px as the FIRST override in this brand-new session.
            cdp_360.send("Emulation.setDeviceMetricsOverride", {
                "width": 360,
                "height": 740,
                "deviceScaleFactor": 1,
                "mobile": True,
                "fitWindow": False
            })
            # Step 2: Now navigate to the real test page.
            cdp_360.send("Page.navigate",
                         {"url": f"http://127.0.0.1:{HTTP_PORT}/test-harness.html"})
            time.sleep(2)
            metrics = cdp_360.evaluate("""
                (() => {
                    // Disable overflow-x: hidden to expose any true layout overflow
                    document.documentElement.style.overflowX = 'visible';
                    document.body.style.overflowX = 'visible';

                    const innerW = window.innerWidth;
                    const scrollW = document.documentElement.scrollWidth;
                    const clientW = document.documentElement.clientWidth;
                    const bodyScrollW = document.body.scrollWidth;

                    return {
                        innerW: innerW,
                        clientW: clientW,
                        scrollW: scrollW,
                        bodyScrollW: bodyScrollW,
                        noOverflow: scrollW <= innerW && bodyScrollW <= innerW
                    };
                })()
            """)
            cdp_360.capture_screenshot(ARTIFACT_DIR / "real_browser_test_harness_360px.png")
        finally:
            if cdp_360:
                cdp_360.close()
            proc_360.terminate()
            try:
                proc_360.wait(timeout=3)
            except Exception:
                proc_360.kill()
            shutil.rmtree(temp_360_profile, ignore_errors=True)

        if metrics:
            print(f"  * window.innerWidth              : {metrics['innerW']}px")
            print(f"  * document.documentElement.scrollWidth: {metrics['scrollW']}px")
            print(f"  * document.body.scrollWidth       : {metrics['bodyScrollW']}px")
            print(f"  * scrollWidth <= innerWidth (with overflow-x: visible): {metrics['noOverflow']}")
            if metrics['innerW'] != 360:
                print(f"  [WARN] innerWidth is {metrics['innerW']}px, expected 360px — test marked FAIL")
            test_results["Test 6: Strict 360px Viewport (scrollWidth <= innerWidth)"] = (
                metrics["noOverflow"] and metrics["innerW"] == 360
            )
        else:
            print("  [ERROR] Could not obtain 360px metrics")
            test_results["Test 6: Strict 360px Viewport (scrollWidth <= innerWidth)"] = False

        # --- TEST 7: Production index.html Verification ---
        print("\n[Test 7] Production index.html Real-Browser Verification:")
        cdp.send("Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"})
        time.sleep(2)

        prod_cards = cdp.evaluate("document.querySelectorAll('.opportunity-card').length")
        prod_results_text = cdp.evaluate("document.getElementById('results-count').textContent.trim()")
        prod_empty_title = cdp.evaluate("""
            (() => {
                const el = document.querySelector('.empty-state-title');
                return el ? el.textContent.trim() : null;
            })()
        """)
        print(f"  * Production Cards Rendered: {prod_cards} (Expected: 0)")
        print(f"  * Results Message          : '{prod_results_text}'")
        print(f"  * Empty State Title        : '{prod_empty_title}'")
        test_results["Test 7: Production index.html (Authentic Empty State)"] = (
            prod_cards == 0 and "لا توجد فرص" in (prod_empty_title or "")
        )
        cdp.capture_screenshot(ARTIFACT_DIR / "real_browser_production_empty.png")

    finally:
        if cdp:
            cdp.close()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        httpd.shutdown()
        shutil.rmtree(temp_profile, ignore_errors=True)

    print("\n" + "=" * 70)
    print("Real-Browser Verification Summary Report:")
    print("=" * 70)
    all_ok = True
    for test_name, passed in test_results.items():
        status_str = "PASS" if passed else "FAIL"
        print(f"  [{status_str}] {test_name}")
        if not passed:
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(run_browser_tests())
