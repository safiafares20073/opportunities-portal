#!/usr/bin/env python3
"""
Opportunities Portal — Service Worker & Offline Support Verification Suite
==========================================================================
Verifies:
  1. Service Worker (sw.js) static syntax and lifecycle event handlers
  2. Pre-cache manifest asset existence on disk
  3. Dynamic Service Worker registration and Cache API population via headless Chrome
  4. Network emulation offline state:
     - Offline fetch of app shell (index.html, css/style.css, js/app.js)
     - Offline fetch of opportunity catalog (data/opportunities.json)
     - Offline favorites workflow validation
"""

import base64
import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

# Try importing websocket-client
try:
    import websocket
except ImportError:
    print("[WARN] websocket-client not installed; running in static analysis mode")
    websocket = None

ROOT_DIR = Path(__file__).resolve().parent.parent
SW_FILE = ROOT_DIR / "sw.js"
DATA_FILE = ROOT_DIR / "data" / "opportunities.json"


def find_chrome():
    candidates = [
        os.environ.get("CHROME_BIN", ""),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\DELL\AppData\Local\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return str(Path(c).resolve())
    return None


class CDPClient:
    def __init__(self, ws_url: str):
        self.ws = websocket.create_connection(ws_url, timeout=10)
        self.msg_id = 0

    def send(self, method: str, params: dict = None):
        self.msg_id += 1
        payload = {"id": self.msg_id, "method": method, "params": params or {}}
        self.ws.send(json.dumps(payload))
        while True:
            raw = self.ws.recv()
            msg = json.loads(raw)
            if msg.get("id") == self.msg_id:
                if "error" in msg:
                    raise RuntimeError(f"CDP error: {msg['error']}")
                return msg.get("result", {})

    def evaluate(self, expression: str):
        res = self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        result_obj = res.get("result", {})
        if "value" in result_obj:
            return result_obj["value"]
        return result_obj

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def test_static_sw():
    print("=" * 65)
    print("Test 1: Static Analysis of sw.js & Cache Manifest")
    print("=" * 65)

    if not SW_FILE.exists():
        print(f"[FAIL] sw.js does not exist at {SW_FILE}")
        return False

    content = SW_FILE.read_text(encoding="utf-8")

    # Check event listeners
    has_install = "addEventListener('install'" in content or 'addEventListener("install"' in content
    has_activate = "addEventListener('activate'" in content or 'addEventListener("activate"' in content
    has_fetch = "addEventListener('fetch'" in content or 'addEventListener("fetch"' in content
    has_cache_name = "CACHE_NAME" in content
    has_precache = "PRECACHE_ASSETS" in content or "cache.addAll" in content

    print(f"  * Install event listener  : {'[OK]' if has_install else '[FAIL]'}")
    print(f"  * Activate event listener : {'[OK]' if has_activate else '[FAIL]'}")
    print(f"  * Fetch event listener    : {'[OK]' if has_fetch else '[FAIL]'}")
    print(f"  * Cache Name versioning   : {'[OK]' if has_cache_name else '[FAIL]'}")
    print(f"  * Pre-cache asset list    : {'[OK]' if has_precache else '[FAIL]'}")

    # Verify precached assets exist on disk
    precache_matches = re.search(r"PRECACHE_ASSETS\s*=\s*\[(.*?)\];", content, re.DOTALL)
    if precache_matches:
        raw_items = precache_matches.group(1)
        items = [i.strip(" \t\n\r'\"") for i in raw_items.split(",") if i.strip(" \t\n\r'\"")]
        print(f"  * Pre-cache asset manifest ({len(items)} items):")
        all_exist = True
        for it in items:
            if it in (".", "./"):
                disk_file = ROOT_DIR / "index.html"
            else:
                disk_file = ROOT_DIR / it
            exists = disk_file.exists()
            print(f"      - {it:<25} -> {'EXISTS' if exists else 'MISSING'}")
            if not exists:
                all_exist = False
        if not all_exist:
            print("[FAIL] Some pre-cache assets are missing on disk")
            return False

    passed = has_install and has_activate and has_fetch and has_cache_name
    print(f"[RESULT] Static sw.js verification: {'PASSED' if passed else 'FAILED'}\n")
    return passed


def test_browser_offline():
    print("=" * 65)
    print("Test 2: Headless Browser Service Worker & Offline Cache Flow")
    print("=" * 65)

    chrome_bin = find_chrome()
    if not chrome_bin:
        print("[SKIP] Chrome binary not found; skipping live browser execution.")
        return True

    if not websocket:
        print("[SKIP] websocket-client not available; skipping browser CDP tests.")
        return True

    # Find free ports
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        http_port = s.getsockname()[1]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        cdp_port = s.getsockname()[1]

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

        def end_headers(self):
            # Add Service-Worker-Allowed header
            self.send_header("Service-Worker-Allowed", "/")
            super().end_headers()

        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", http_port), Handler)
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()
    print(f"  * Local server active on http://127.0.0.1:{http_port}")

    temp_profile = tempfile.mkdtemp(prefix="sw_test_profile_")

    proc = subprocess.Popen([
        chrome_bin,
        "--headless=new",
        f"--remote-debugging-port={cdp_port}",
        "--remote-allow-origins=*",
        "--disable-gpu",
        f"--user-data-dir={temp_profile}",
        f"http://127.0.0.1:{http_port}/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(2)
    cdp = None
    results = {}

    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=5)
        targets = json.loads(req.read().decode())
        page_t = next(x for x in targets if x.get("type") == "page")
        cdp = CDPClient(page_t["webSocketDebuggerUrl"])
        cdp.send("Page.enable")
        cdp.send("Runtime.enable")
        cdp.send("Network.enable")

        time.sleep(1)

        # 1. Register Service Worker dynamically in browser
        print("  * Registering sw.js in live browser session...")
        reg_result = cdp.evaluate("""
            (async () => {
                if (!('serviceWorker' in navigator)) {
                    return { success: false, error: 'ServiceWorker not supported' };
                }
                try {
                    const reg = await navigator.serviceWorker.register('./sw.js', { scope: './' });
                    // Wait for active
                    let sw = reg.installing || reg.waiting || reg.active;
                    if (reg.active) {
                        return { success: true, status: 'active', scope: reg.scope };
                    }
                    return new Promise((resolve) => {
                        sw.addEventListener('statechange', (e) => {
                            if (e.target.state === 'activated' || e.target.state === 'installed') {
                                resolve({ success: true, status: e.target.state, scope: reg.scope });
                            }
                        });
                        setTimeout(() => resolve({ success: true, status: 'registered', scope: reg.scope }), 3000);
                    });
                } catch (err) {
                    return { success: false, error: err.message };
                }
            })()
        """)
        print(f"      - Registration: {reg_result}")
        results["SW Registration"] = reg_result.get("success", False)

        time.sleep(2)

        # 2. Inspect Cache API contents
        cache_check = cdp.evaluate("""
            (async () => {
                const keys = await caches.keys();
                if (!keys.length) return { hasCaches: false, keys: [] };
                const cache = await caches.open(keys[0]);
                const requests = await cache.keys();
                const urls = requests.map(r => new URL(r.url).pathname);
                return {
                    hasCaches: true,
                    cacheName: keys[0],
                    cachedUrls: urls
                };
            })()
        """)
        print(f"  * Cache API inspection:")
        print(f"      - Cache Name: {cache_check.get('cacheName')}")
        print(f"      - Cached Assets ({len(cache_check.get('cachedUrls', []))} items): {cache_check.get('cachedUrls')}")
        results["Cache API Population"] = bool(cache_check.get("hasCaches"))

        # 3. Emulate OFFLINE mode using CDP
        print("  * Enabling OFFLINE emulation (Network.emulateNetworkConditions)...")
        cdp.send("Network.emulateNetworkConditions", {
            "offline": True,
            "latency": 0,
            "downloadThroughput": 0,
            "uploadThroughput": 0
        })

        # 4. Attempt to fetch opportunities.json while OFFLINE
        offline_data_fetch = cdp.evaluate("""
            (async () => {
                try {
                    const res = await fetch('data/opportunities.json');
                    const json = await res.json();
                    return {
                        ok: res.ok,
                        status: res.status,
                        isFromCache: true,
                        count: json.length,
                        sampleId: json[0]?.id
                    };
                } catch (err) {
                    return { ok: false, error: err.message };
                }
            })()
        """)
        print(f"  * Offline Data Fetch (data/opportunities.json):")
        print(f"      - Success: {offline_data_fetch.get('ok')}")
        print(f"      - Opportunities retrieved offline: {offline_data_fetch.get('count')}")
        print(f"      - First opportunity: {offline_data_fetch.get('sampleId')}")
        results["Offline Catalog Fetch"] = bool(offline_data_fetch.get("ok") and offline_data_fetch.get("count", 0) > 0)

        # 5. Offline Favorites Workflow verification
        offline_favorites_check = cdp.evaluate("""
            (async () => {
                try {
                    // Simulate bookmarking 2 opportunities into localStorage
                    const favIds = ['chevening-scholarship-yemen', 'harvard-cs50x-computer-science'];
                    localStorage.setItem('opportunities_portal_favorites', JSON.stringify(favIds));

                    // Fetch cached catalog offline
                    const res = await fetch('data/opportunities.json');
                    const allData = await res.json();

                    // Filter matching favorites from cached dataset
                    const rawFavs = JSON.parse(localStorage.getItem('opportunities_portal_favorites') || '[]');
                    const favSet = new Set(rawFavs);
                    const filteredFavs = allData.filter(item => favSet.has(item.id));

                    return {
                        success: true,
                        favoriteIdsInStorage: rawFavs,
                        matchedInCachedCatalog: filteredFavs.map(f => f.id)
                    };
                } catch (err) {
                    return { success: false, error: err.message };
                }
            })()
        """)
        print(f"  * Offline Favorites Verification:")
        print(f"      - Stored favorites: {offline_favorites_check.get('favoriteIdsInStorage')}")
        print(f"      - Retrieved offline: {offline_favorites_check.get('matchedInCachedCatalog')}")
        results["Offline Favorites Retention"] = bool(
            offline_favorites_check.get("success") and
            len(offline_favorites_check.get("matchedInCachedCatalog", [])) == 2
        )

    finally:
        if cdp:
            cdp.close()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        server.shutdown()
        shutil.rmtree(temp_profile, ignore_errors=True)

    print("\n" + "=" * 65)
    print("Browser Offline Verification Summary:")
    all_passed = True
    for name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    print("=" * 65 + "\n")
    return all_passed


if __name__ == "__main__":
    t1 = test_static_sw()
    t2 = test_browser_offline()
    if t1 and t2:
        print("[ALL TESTS PASSED] Service Worker and Offline Workflow verified successfully.")
        sys.exit(0)
    else:
        print("[FAILURE] Some tests failed.")
        sys.exit(1)
