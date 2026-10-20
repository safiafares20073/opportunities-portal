import http.server
import json
import shutil
import socket
import socketserver
import subprocess
import tempfile
import threading
import time
import urllib.request
import websocket
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        pass


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("127.0.0.1", 0), QuietHandler)
http_port = httpd.server_address[1]
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
time.sleep(1)

cdp_port = get_free_port()
temp_profile = tempfile.mkdtemp(prefix="chrome_overflow_")

# Start Chrome with about:blank so that setDeviceMetricsOverride(360) is the
# FIRST and ONLY override applied in this session.  Navigating to the real
# page URL at launch would place the page in a 762px-wide headless window
# before any emulation is set, causing Chrome to return 440px instead of 360px.
chrome_cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--headless=new",
    f"--remote-debugging-port={cdp_port}",
    "--remote-allow-origins=*",
    "--disable-gpu",
    f"--user-data-dir={temp_profile}",
    "about:blank"
]

proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
try:
    req = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=5)
    targets = json.loads(req.read().decode())
    target = next(t for t in targets if t.get("type") == "page")
    ws = websocket.create_connection(target["webSocketDebuggerUrl"])

    msg_id = 0

    def send(method, params=None):
        global msg_id
        msg_id += 1
        ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        while True:
            raw = ws.recv()
            data = json.loads(raw)
            if data.get("id") == msg_id:
                if "error" in data:
                    raise RuntimeError(f"CDP Error ({method}): {data['error']}")
                return data.get("result", {})

    def evaluate(expr):
        res_obj = send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in res_obj:
            raise RuntimeError(f"CDP Exception: {res_obj['exceptionDetails']}")
        inner = res_obj.get("result", {})
        if "value" in inner:
            return inner["value"]
        if "value" in res_obj:
            return res_obj["value"]
        return inner or res_obj

    # Step 1: Enable domains
    send("Page.enable")
    send("Runtime.enable")
    send("DOM.enable")

    # Step 2: Set 360px override BEFORE navigating to any real page.
    #         This is the key fix — override must be the first metric applied.
    send("Emulation.setDeviceMetricsOverride", {
        "width": 360,
        "height": 740,
        "deviceScaleFactor": 1,
        "mobile": True,
        "fitWindow": False
    })

    # Step 3: Now navigate to the real test page.
    send("Page.navigate", {"url": f"http://127.0.0.1:{http_port}/test-harness.html"})
    # Wait for page and fixtures to fully render
    time.sleep(2)

    # Check widths without overflow-x: hidden
    res = evaluate("""
        (() => {
            // Temporarily disable overflow-x: hidden to expose any true overflow
            document.body.style.overflowX = 'visible';
            document.documentElement.style.overflowX = 'visible';

            const innerW = window.innerWidth;
            const scrollW = document.documentElement.scrollWidth;
            const bodyScrollW = document.body.scrollWidth;

            // Find any element exceeding innerW
            const overflowingElements = [];
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                const rect = el.getBoundingClientRect();
                if (rect.width > innerW + 1) {
                    overflowingElements.push({
                        tag: el.tagName,
                        className: el.className,
                        id: el.id,
                        width: rect.width,
                        scrollWidth: el.scrollWidth
                    });
                }
            }

            return {
                innerW: innerW,
                scrollW: scrollW,
                bodyScrollW: bodyScrollW,
                hasOverflow: scrollW > innerW,
                overflowingElements: overflowingElements
            };
        })()
    """)
    print("360px Direct Window Width Test Results:")
    print(json.dumps(res, indent=2, ensure_ascii=False))

finally:
    try:
        ws.close()
    except Exception:
        pass
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
    httpd.shutdown()
    httpd.server_close()
    shutil.rmtree(temp_profile, ignore_errors=True)
