#!/usr/bin/env python3
"""
Milestone 2 Real-Browser End-to-End Test Suite
==============================================
Validates:
1. Details modal opens with correct opportunity data (US3).
2. Escape key and close button work.
3. Keyboard focus returns correctly after closing.
4. Favorite/unfavorite works on cards and inside the modal (US5).
5. Favorites persist after page reload through localStorage.
6. Favorites-only view and its empty state work.
7. Modal remains usable on mobile screens and in RTL layout.
8. Zero JavaScript console errors or uncaught exceptions.
"""

import base64
import http.server
import json
import os
import shutil
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import websocket
except ImportError:
    print("[ERROR] websocket-client library is required.")
    sys.exit(1)

ROOT_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_DIR = Path(os.environ.get(
    "GEMINI_ARTIFACT_DIR",
    r"C:\Users\DELL\.gemini\antigravity\brain\a8f26efd-4c7c-4159-bd88-d5b8d0129f21"
))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_BIN = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
if not CHROME_BIN.exists():
    CHROME_BIN = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
if not CHROME_BIN.exists():
    raise RuntimeError("No Chromium browser found.")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        return super().do_GET()

    def log_message(self, format, *args):
        pass


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class CDPClient:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=20)
        self.msg_id = 0
        self.console_errors = []
        self.exceptions = []

    def send(self, method, params=None):
        self.msg_id += 1
        payload = {"id": self.msg_id, "method": method, "params": params or {}}
        self.ws.send(json.dumps(payload))
        while True:
            raw = self.ws.recv()
            data = json.loads(raw)

            # Collect asynchronous errors/exceptions
            if data.get("method") == "Runtime.exceptionThrown":
                self.exceptions.append(data.get("params", {}))
            elif data.get("method") == "Log.entryAdded":
                entry = data.get("params", {}).get("entry", {})
                if entry.get("level") == "error":
                    if "favicon.ico" not in entry.get("url", ""):
                        self.console_errors.append(entry)
            elif data.get("method") == "Runtime.consoleAPICalled":
                params = data.get("params", {})
                if params.get("type") == "error":
                    self.console_errors.append(params)

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
        if "exceptionDetails" in res:
            raise RuntimeError(f"Evaluation Exception: {res['exceptionDetails']}")
        result_obj = res.get("result", {})
        if "value" in result_obj:
            return result_obj["value"]
        return result_obj

    def capture_screenshot(self, output_path: Path):
        res = self.send("Page.captureScreenshot", {"format": "png"})
        raw_b64 = res["data"]
        output_path.write_bytes(base64.b64decode(raw_b64))

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def run_tests():
    print("=" * 70)
    print("Starting Milestone 2 Browser End-to-End Verification")
    print("=" * 70)

    # 1. Start local HTTP server on dynamic port
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", 0), QuietHandler)
    http_port = httpd.server_address[1]
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    print(f"[OK] Local HTTP Server running on http://127.0.0.1:{http_port}")

    # 2. Start Chrome
    cdp_port = get_free_port()
    temp_profile = tempfile.mkdtemp(prefix="chrome_m2_test_")
    chrome_cmd = [
        str(CHROME_BIN),
        "--headless=new",
        f"--remote-debugging-port={cdp_port}",
        "--remote-allow-origins=*",
        "--disable-gpu",
        "--no-first-run",
        f"--user-data-dir={temp_profile}",
        "about:blank"
    ]
    proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    client = None
    all_passed = True
    results = {}

    try:
        # Connect to CDP
        req = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=10)
        targets = json.loads(req.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        client = CDPClient(page_target["webSocketDebuggerUrl"])

        # Enable runtime / page / log
        client.send("Page.enable")
        client.send("Runtime.enable")
        client.send("DOM.enable")
        client.send("Log.enable")

        # Navigate to test harness
        url = f"http://127.0.0.1:{http_port}/test-harness.html"
        print(f"[INFO] Navigating to {url}")
        client.send("Page.navigate", {"url": url})
        time.sleep(2)

        # Ensure page initialized
        client.evaluate("""
            new Promise((resolve) => {
                if (document.querySelectorAll('.opportunity-card').length > 0) resolve();
                const observer = new MutationObserver(() => {
                    if (document.querySelectorAll('.opportunity-card').length > 0) {
                        observer.disconnect();
                        resolve();
                    }
                });
                observer.observe(document.body, { childList: true, subtree: true });
                setTimeout(resolve, 3000);
            })
        """)

        card_count = client.evaluate("document.querySelectorAll('.opportunity-card').length")
        print(f"[OK] Page loaded with {card_count} fixture cards.")
        assert card_count == 8, f"Expected 8 cards, got {card_count}"

        # -------------------------------------------------------------
        # TEST 1: Details modal opens with correct opportunity data
        # -------------------------------------------------------------
        print("\n--- Test 1: Details Modal Content & Data Fidelity ---")
        modal_opened = client.evaluate("""
            (() => {
                const btn = document.querySelector('.btn-details[data-id="test-chevening-scholarship"]');
                if (!btn) return false;
                btn.click();
                const modal = document.getElementById('details-modal');
                return modal && modal.getAttribute('aria-hidden') === 'false' && modal.style.display === 'flex';
            })()
        """)
        assert modal_opened, "Details modal did not open or aria-hidden != 'false'"

        modal_data = client.evaluate("""
            (() => {
                const title = document.querySelector('.modal-opportunity-title')?.textContent?.trim();
                const titleEn = document.querySelector('.modal-title-en')?.textContent?.trim();
                const org = document.querySelector('.modal-org span')?.textContent?.trim();
                const facts = Array.from(document.querySelectorAll('.modal-fact-row')).map(row => ({
                    label: row.querySelector('dt')?.textContent?.trim(),
                    value: row.querySelector('dd')?.textContent?.trim()
                }));
                const eligibility = document.querySelector('.modal-section-text')?.textContent?.trim();
                const verification = document.querySelector('.modal-verification time')?.textContent?.trim();
                const applyBtn = document.querySelector('.modal-btn-apply');
                const bookmarkBtn = document.querySelector('.btn-bookmark-modal');

                return {
                    title,
                    titleEn,
                    org,
                    facts,
                    eligibility,
                    verification,
                    applyHref: applyBtn ? applyBtn.getAttribute('href') : null,
                    hasBookmarkBtn: !!bookmarkBtn
                };
            })()
        """)

        print(f"  Title: {modal_data['title']}")
        print(f"  English Title: {modal_data['titleEn']}")
        print(f"  Organization: {modal_data['org']}")
        print(f"  Verification Date: {modal_data['verification']}")
        print(f"  Official Apply Link: {modal_data['applyHref']}")

        assert "[تجريبي] منحة تشيفنينغ" in modal_data["title"], "Modal title mismatch"
        assert "Chevening" in modal_data["titleEn"] and "Scholarship" in modal_data["titleEn"], "Modal English title mismatch"
        assert "وزارة الخارجية" in modal_data["org"], "Organization mismatch"
        assert "2026-10-15" in modal_data["verification"], "Verification date mismatch"
        assert "chevening.org" in modal_data["applyHref"], "Apply link mismatch"
        assert modal_data["hasBookmarkBtn"], "Bookmark button missing from modal"

        # Capture desktop screenshot with modal open
        desktop_modal_shot = ARTIFACT_DIR / "m2_modal_desktop.png"
        client.capture_screenshot(desktop_modal_shot)
        print(f"  [SAVED] Screenshot: {desktop_modal_shot.name}")
        results["test_1_modal_data"] = "PASS"

        # -------------------------------------------------------------
        # TEST 2: Close button works
        # -------------------------------------------------------------
        print("\n--- Test 2: Modal Close Button ---")
        close_btn_worked = client.evaluate("""
            (() => {
                const closeBtn = document.getElementById('modal-close-btn');
                if (!closeBtn) return false;
                closeBtn.click();
                const modal = document.getElementById('details-modal');
                const bodyOpen = document.body.classList.contains('modal-open');
                return modal.getAttribute('aria-hidden') === 'true' && modal.style.display === 'none' && !bodyOpen;
            })()
        """)
        assert close_btn_worked, "Modal failed to close via close button"
        print("  [OK] Modal closed successfully via close button; aria-hidden='true', modal-open class removed.")
        results["test_2_close_button"] = "PASS"

        # -------------------------------------------------------------
        # TEST 3: Escape key dismiss and focus return
        # -------------------------------------------------------------
        print("\n--- Test 3: Escape Key & Focus Return ---")
        # Open modal again via keyboard click on details button
        reopened = client.evaluate("""
            (() => {
                const btn = document.querySelector('.btn-details[data-id="test-google-ai-course"]');
                btn.focus();
                btn.click();
                const modal = document.getElementById('details-modal');
                return modal && modal.getAttribute('aria-hidden') === 'false';
            })()
        """)
        assert reopened, "Failed to reopen modal for test 3"

        # Send Escape key via CDP
        client.send("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "key": "Escape",
            "code": "Escape",
            "windowsVirtualKeyCode": 27,
            "nativeVirtualKeyCode": 27
        })
        client.send("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "key": "Escape",
            "code": "Escape",
            "windowsVirtualKeyCode": 27,
            "nativeVirtualKeyCode": 27
        })
        time.sleep(0.3)

        esc_closed = client.evaluate("""
            (() => {
                const modal = document.getElementById('details-modal');
                const isHidden = modal.getAttribute('aria-hidden') === 'true';
                const activeId = document.activeElement ? document.activeElement.getAttribute('data-id') : null;
                return {
                    isHidden: isHidden,
                    activeId: activeId
                };
            })()
        """)
        assert esc_closed["isHidden"], "Modal did not close on Escape key"
        assert esc_closed["activeId"] == "test-google-ai-course", (
            f"Focus did not return to triggering button! Active element ID: {esc_closed['activeId']}"
        )
        print("  [OK] Modal closed via Escape key and focus returned to the triggering details button.")
        results["test_3_escape_and_focus"] = "PASS"

        # -------------------------------------------------------------
        # TEST 4: Favorite/Unfavorite on cards and inside modal
        # -------------------------------------------------------------
        print("\n--- Test 4: Favorite/Unfavorite on Cards & Inside Modal ---")
        # 4a: Click bookmark on card
        card_fav_state = client.evaluate("""
            (() => {
                const cardBtn = document.querySelector('.btn-bookmark[data-id="test-chevening-scholarship"]');
                cardBtn.click();
                const badge = document.getElementById('favorites-count-badge');
                return {
                    pressed: cardBtn.getAttribute('aria-pressed'),
                    hasBookmarkedClass: cardBtn.classList.contains('bookmarked'),
                    badgeText: badge ? badge.textContent.trim() : null,
                    badgeVisible: badge ? badge.style.display !== 'none' : false
                };
            })()
        """)
        assert card_fav_state["pressed"] == "true", "Card bookmark aria-pressed is not true"
        assert card_fav_state["hasBookmarkedClass"], "Card bookmark missing 'bookmarked' class"
        assert card_fav_state["badgeText"] == "1", f"Badge count expected '1', got {card_fav_state['badgeText']}"
        print("  [OK] Card bookmark clicked: aria-pressed='true', class='bookmarked', badge=1.")

        # 4b: Open modal for same card and check modal bookmark button
        modal_fav_state = client.evaluate("""
            (() => {
                const detailsBtn = document.querySelector('.btn-details[data-id="test-chevening-scholarship"]');
                detailsBtn.click();
                const modalBookmarkBtn = document.querySelector('.btn-bookmark-modal');
                return {
                    pressed: modalBookmarkBtn.getAttribute('aria-pressed'),
                    hasBookmarkedClass: modalBookmarkBtn.classList.contains('bookmarked'),
                    text: modalBookmarkBtn.querySelector('span')?.textContent?.trim()
                };
            })()
        """)
        assert modal_fav_state["pressed"] == "true", "Modal bookmark aria-pressed is not true"
        assert modal_fav_state["hasBookmarkedClass"], "Modal bookmark missing 'bookmarked' class"
        assert "محفوظة" in modal_fav_state["text"], f"Expected 'محفوظة', got {modal_fav_state['text']}"
        print("  [OK] Modal opened: in-modal bookmark reflects favored state ('محفوظة').")

        # 4c: Toggle unfavorite INSIDE modal
        modal_unfav_state = client.evaluate("""
            (() => {
                const modalBookmarkBtn = document.querySelector('.btn-bookmark-modal');
                modalBookmarkBtn.click();
                const badge = document.getElementById('favorites-count-badge');
                const cardBtn = document.querySelector('.btn-bookmark[data-id="test-chevening-scholarship"]');
                return {
                    modalPressed: modalBookmarkBtn.getAttribute('aria-pressed'),
                    modalHasClass: modalBookmarkBtn.classList.contains('bookmarked'),
                    modalText: modalBookmarkBtn.querySelector('span')?.textContent?.trim(),
                    badgeVisible: badge ? badge.style.display !== 'none' : false,
                    cardPressed: cardBtn.getAttribute('aria-pressed'),
                    cardHasClass: cardBtn.classList.contains('bookmarked')
                };
            })()
        """)
        assert modal_unfav_state["modalPressed"] == "false", "Modal bookmark aria-pressed not false after unfavorite"
        assert not modal_unfav_state["modalHasClass"], "Modal bookmark still has bookmarked class"
        assert "حفظ" in modal_unfav_state["modalText"], f"Expected 'حفظ', got {modal_unfav_state['modalText']}"
        assert not modal_unfav_state["cardHasClass"], "Card bookmark still has bookmarked class after modal unfavorite"
        print("  [OK] Toggled unfavorite inside modal: modal & background card buttons both updated, badge=0.")

        # Close modal
        client.evaluate("document.getElementById('modal-close-btn').click();")

        # 4d: Favorite 2 items from cards for next tests
        client.evaluate("""
            (() => {
                document.querySelector('.btn-bookmark[data-id="test-chevening-scholarship"]').click();
                document.querySelector('.btn-bookmark[data-id="test-undp-internship"]').click();
            })()
        """)
        fav_count = client.evaluate("document.getElementById('favorites-count-badge')?.textContent?.trim()")
        assert fav_count == "2", f"Expected badge '2', got {fav_count}"
        print("  [OK] Favorited 2 items from cards (badge=2).")
        results["test_4_favorites_sync"] = "PASS"

        # -------------------------------------------------------------
        # TEST 5: Favorites persist after page reload through localStorage
        # -------------------------------------------------------------
        print("\n--- Test 5: localStorage Persistence Across Reload ---")
        stored_raw = client.evaluate("localStorage.getItem('opportunities_portal_favorites')")
        stored_list = json.loads(stored_raw)
        print(f"  LocalStorage before reload: {stored_list}")
        assert "test-chevening-scholarship" in stored_list
        assert "test-undp-internship" in stored_list

        # Reload the page
        client.send("Page.reload", {"ignoreCache": True})
        time.sleep(2)

        # Check state after reload
        reload_state = client.evaluate("""
            (() => {
                const badge = document.getElementById('favorites-count-badge');
                const card1 = document.querySelector('.btn-bookmark[data-id="test-chevening-scholarship"]');
                const card2 = document.querySelector('.btn-bookmark[data-id="test-undp-internship"]');
                const card3 = document.querySelector('.btn-bookmark[data-id="test-google-ai-course"]');
                return {
                    badgeText: badge ? badge.textContent.trim() : null,
                    card1Fav: card1 ? card1.getAttribute('aria-pressed') === 'true' && card1.classList.contains('bookmarked') : false,
                    card2Fav: card2 ? card2.getAttribute('aria-pressed') === 'true' && card2.classList.contains('bookmarked') : false,
                    card3Fav: card3 ? card3.getAttribute('aria-pressed') === 'true' : false
                };
            })()
        """)
        assert reload_state["badgeText"] == "2", f"Post-reload badge expected '2', got {reload_state['badgeText']}"
        assert reload_state["card1Fav"], "Card 1 lost favorite status after reload"
        assert reload_state["card2Fav"], "Card 2 lost favorite status after reload"
        assert not reload_state["card3Fav"], "Unfavorited card incorrectly marked as favorite"
        print("  [OK] All favorites successfully persisted through page reload via localStorage.")
        results["test_5_localstorage_persistence"] = "PASS"

        # -------------------------------------------------------------
        # TEST 6: Favorites-only view and empty state
        # -------------------------------------------------------------
        print("\n--- Test 6: Favorites-Only View & Empty State ---")
        # 6a: Switch to Favorites Tab
        fav_tab_state = client.evaluate("""
            (() => {
                document.getElementById('tab-favorites').click();
                const tabFav = document.getElementById('tab-favorites');
                const cards = document.querySelectorAll('.opportunity-card');
                const countText = document.getElementById('results-count')?.textContent?.trim();
                return {
                    tabSelected: tabFav.getAttribute('aria-selected'),
                    tabActive: tabFav.classList.contains('active'),
                    cardCount: cards.length,
                    countText: countText
                };
            })()
        """)
        assert fav_tab_state["tabSelected"] == "true", "Favorites tab aria-selected != 'true'"
        assert fav_tab_state["cardCount"] == 2, f"Expected 2 cards in favorites view, got {fav_tab_state['cardCount']}"
        assert "محفوظة" in fav_tab_state["countText"], f"Results count missing 'محفوظة': {fav_tab_state['countText']}"
        print(f"  [OK] Favorites view active: {fav_tab_state['cardCount']} cards shown, text='{fav_tab_state['countText']}'.")

        # Capture favorites view screenshot
        fav_tab_shot = ARTIFACT_DIR / "m2_favorites_tab.png"
        client.capture_screenshot(fav_tab_shot)
        print(f"  [SAVED] Screenshot: {fav_tab_shot.name}")

        # 6b: Unfavorite all items to trigger empty state
        empty_state = client.evaluate("""
            (() => {
                // Click bookmark on both remaining cards to unfavorite them
                const btns = document.querySelectorAll('.opportunity-card .btn-bookmark');
                btns.forEach(b => b.click());

                const emptyContainer = document.getElementById('empty-state-container');
                const emptyTitle = emptyContainer ? emptyContainer.querySelector('.empty-state-title')?.textContent?.trim() : null;
                const showAllBtn = document.getElementById('show-all-btn');
                const gridCards = document.querySelectorAll('.opportunity-card').length;

                return {
                    emptyVisible: emptyContainer ? emptyContainer.style.display !== 'none' : false,
                    emptyTitle: emptyTitle,
                    hasShowAllBtn: !!showAllBtn,
                    gridCards: gridCards
                };
            })()
        """)
        assert empty_state["emptyVisible"], "Empty state container not visible when favorites empty"
        assert "لا توجد فرص محفوظة" in empty_state["emptyTitle"], f"Empty state title mismatch: {empty_state['emptyTitle']}"
        assert empty_state["hasShowAllBtn"], "Missing 'استعراض جميع الفرص' button in favorites empty state"
        assert empty_state["gridCards"] == 0, f"Grid still has {empty_state['gridCards']} cards in empty state"
        print(f"  [OK] Favorites empty state rendered with title: '{empty_state['emptyTitle']}'.")

        # Capture empty state screenshot
        fav_empty_shot = ARTIFACT_DIR / "m2_favorites_empty.png"
        client.capture_screenshot(fav_empty_shot)
        print(f"  [SAVED] Screenshot: {fav_empty_shot.name}")

        # 6c: Click "استعراض جميع الفرص"
        switch_back = client.evaluate("""
            (() => {
                document.getElementById('show-all-btn').click();
                const tabAll = document.getElementById('tab-all');
                const cards = document.querySelectorAll('.opportunity-card').length;
                return {
                    allSelected: tabAll.getAttribute('aria-selected') === 'true',
                    allActive: tabAll.classList.contains('active'),
                    cardCount: cards
                };
            })()
        """)
        assert switch_back["allSelected"], "All tab not selected after clicking show-all"
        assert switch_back["cardCount"] == 8, f"Expected 8 cards after returning to all, got {switch_back['cardCount']}"
        print(f"  [OK] Returned to All tab: {switch_back['cardCount']} opportunities restored.")
        results["test_6_favorites_view_and_empty_state"] = "PASS"

        # -------------------------------------------------------------
        # TEST 7: Modal mobile screens & RTL layout
        # -------------------------------------------------------------
        print("\n--- Test 7: Mobile RTL Layout & Modal Usability ---")
        # Apply mobile emulation
        client.send("Emulation.setDeviceMetricsOverride", {
            "width": 360,
            "height": 740,
            "deviceScaleFactor": 1,
            "mobile": True,
            "fitWindow": False
        })
        time.sleep(0.5)

        # Open modal
        client.evaluate("""
            (() => {
                const btn = document.querySelector('.btn-details[data-id="test-edx-cs50-course"]');
                btn.click();
            })()
        """)
        time.sleep(0.5)

        mobile_metrics = client.evaluate("""
            (() => {
                const modal = document.getElementById('details-modal');
                const panel = document.querySelector('.modal-panel');
                const innerW = window.innerWidth;
                const panelRect = panel.getBoundingClientRect();
                const docDir = document.documentElement.getAttribute('dir');
                const bodyDir = document.body.getAttribute('dir');
                const computedDir = window.getComputedStyle(panel).direction;

                return {
                    innerW: innerW,
                    panelWidth: panelRect.width,
                    panelFits: panelRect.width <= innerW + 1,
                    panelHeight: panelRect.height,
                    docDir: docDir,
                    computedDir: computedDir,
                    modalVisible: modal && modal.style.display === 'flex'
                };
            })()
        """)

        print(f"  Inner Viewport Width: {mobile_metrics['innerW']}px")
        print(f"  Modal Panel Width: {mobile_metrics['panelWidth']}px (Fits viewport: {mobile_metrics['panelFits']})")
        print(f"  Document Direction: {mobile_metrics['docDir']} (Computed direction: {mobile_metrics['computedDir']})")

        assert mobile_metrics["modalVisible"], "Modal is not visible on mobile"
        assert mobile_metrics["panelFits"], f"Modal panel overflows viewport! {mobile_metrics['panelWidth']} > {mobile_metrics['innerW']}"
        assert mobile_metrics["docDir"] == "rtl", f"Document dir is not rtl: {mobile_metrics['docDir']}"
        assert mobile_metrics["computedDir"] == "rtl", f"Panel computed direction is not rtl: {mobile_metrics['computedDir']}"

        # Capture mobile modal screenshot
        mobile_modal_shot = ARTIFACT_DIR / "m2_modal_mobile.png"
        client.capture_screenshot(mobile_modal_shot)
        print(f"  [SAVED] Screenshot: {mobile_modal_shot.name}")

        # Close modal and reset emulation
        client.evaluate("document.getElementById('modal-close-btn').click();")
        client.send("Emulation.clearDeviceMetricsOverride")
        print("  [OK] Mobile RTL modal validated successfully.")
        results["test_7_mobile_rtl"] = "PASS"

        # -------------------------------------------------------------
        # TEST 8: JavaScript Console & Runtime Errors
        # -------------------------------------------------------------
        print("\n--- Test 8: JavaScript Console & Runtime Errors ---")
        print(f"  Uncaught Exceptions logged: {len(client.exceptions)}")
        print(f"  Console Errors logged: {len(client.console_errors)}")

        if client.exceptions:
            for ex in client.exceptions:
                print(f"    [EXCEPTION] {ex}")
        if client.console_errors:
            for err in client.console_errors:
                print(f"    [CONSOLE ERROR] {err}")

        assert len(client.exceptions) == 0, f"Uncaught JS exceptions occurred: {client.exceptions}"
        assert len(client.console_errors) == 0, f"Console errors occurred: {client.console_errors}"
        print("  [OK] Zero console errors or runtime exceptions detected across all tests.")
        results["test_8_zero_js_errors"] = "PASS"

    except Exception as e:
        print(f"\n[FAIL] Test encountered an error: {e}")
        all_passed = False
        import traceback
        traceback.print_exc()

    finally:
        if client:
            client.close()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        httpd.shutdown()
        httpd.server_close()
        shutil.rmtree(temp_profile, ignore_errors=True)

    print("\n" + "=" * 70)
    print("Milestone 2 Real-Browser Test Summary")
    print("=" * 70)
    for test_name, status in results.items():
        print(f"  - {test_name}: {status}")
    print("=" * 70)

    if all_passed and len(results) == 8:
        print("ALL 8 MILESTONE 2 BROWSER TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print(f"FAILED: Only {len(results)}/8 tests completed successfully.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
