"""Verify the bridge survives a client that disconnects mid-stream.

Monkeypatches the CLI runner with a slow fake, then:
1. POSTs a streaming request and aborts the client after 3s (mid-run).
2. Asserts: server still answers /health, no traceback in stderr.
3. Also POSTs a full streaming request to completion and asserts SSE output.
"""
import io
import json
import sys
import threading
import time
from contextlib import redirect_stderr
from http.server import ThreadingHTTPServer

import bridge

PORT = 8329


def fake_run(model, prompt, max_turns=1, keepalive_callback=None):
    for _ in range(6):
        time.sleep(1)
        if keepalive_callback:
            keepalive_callback()
    return "simulated full response"


bridge.run_command_code = fake_run
server = ThreadingHTTPServer(("127.0.0.1", PORT), bridge.Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

body = json.dumps({
    "model": "command-code",
    "stream": True,
    "messages": [{"role": "user", "content": "long prompt"}],
}).encode()

failures = []

# 1. Aborted client: server must not crash, no traceback to stderr.
err = io.StringIO()
try:
    import urllib.request

    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with redirect_stderr(err):
        try:
            with urllib.request.urlopen(req, timeout=2) as resp:
                resp.read()
        except Exception:
            pass  # client-side abort is expected here
finally:
    time.sleep(1.5)  # let the server thread finish handling the reset

stderr_txt = err.getvalue()
if "Traceback" in stderr_txt or "Exception occurred" in stderr_txt:
    failures.append(f"server crashed on client disconnect:\n{stderr_txt}")

# 2. Health after the abort.
import urllib.request

try:
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=5) as r:
        ok = json.loads(r.read())
    if not ok.get("ok"):
        failures.append("health check not ok after abort")
except Exception as exc:
    failures.append(f"server unreachable after abort: {exc}")

# 3. Full streaming run still produces proper SSE.
try:
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        sse = r.read().decode()
    if "data: [DONE]" not in sse:
        failures.append("missing [DONE] terminator")
    if "simulated full response" not in sse:
        failures.append("missing content in SSE body")
    if "keepalive" not in sse:
        # keepalive comment only appears if run took >15s; fake runs 6s so
        # its absence is fine here, but record it for visibility
        pass
except Exception as exc:
    failures.append(f"full stream failed: {exc}")

server.shutdown()
server.server_close()

if failures:
    print("FAIL:")
    for f in failures:
        print("-", f)
    sys.exit(1)
print("PASS: no crash on client disconnect; stream completes with [DONE]")