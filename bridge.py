#!/usr/bin/env python3
"""OpenAI-compatible bridge for Command Code CLI models.

This exposes /v1/models and /v1/chat/completions, then delegates each request to
`cmd -p --model ...`. It is intentionally simple because Command Code's Go-plan
Provider API returns 403, while the CLI itself can use the included open-model
credits.
"""

from __future__ import annotations
import threading

import json
import os
import re
import subprocess
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

try:
    import winpty
    HAS_WINPTY = True
except ImportError:
    HAS_WINPTY = False
    if os.name == "nt":
        print("Warning: winpty not installed. Install with: pip install pywinpty", file=sys.stderr)

from config import load_config

MODELS = [
    "deepseek/deepseek-v4-pro",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "MiniMaxAI/MiniMax-M3",
    "xiaomi/mimo-v2.5-pro",
]

ALIASES = {
    "commandcode": "deepseek/deepseek-v4-flash",
    "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
    "deepseek-v4-flash": "deepseek/deepseek-v4-flash",
    "nemotron-3-ultra": "nvidia/nemotron-3-ultra-550b-a55b",
    "nemotron-3-ultra-550b-a55b": "nvidia/nemotron-3-ultra-550b-a55b",
    "minimax-m3": "MiniMaxAI/MiniMax-M3",
    "mimo-v2.5-pro": "xiaomi/mimo-v2.5-pro",
}

CONFIG = load_config()

def resolve_cmd_bin() -> str:
    env_bin = CONFIG.get("COMMAND_CODE_BIN")
    if env_bin:
        if os.name == "nt" and env_bin in {"cmd", "cmd.cmd", "cmd.exe"}:
            appdata = os.environ.get("APPDATA", "")
            npm_cmd = os.path.join(appdata, "npm", "cmd.cmd")
            if os.path.exists(npm_cmd):
                return npm_cmd
        return env_bin

    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        for name in ["command-code.cmd", "cmd.cmd", "commandcode.cmd", "cmdc.cmd"]:
            p = os.path.join(appdata, "npm", name)
            if os.path.exists(p):
                return p
        return "command-code.cmd"
    return "/home/deploy/.npm-global/bin/cmd"


CMD_BIN = resolve_cmd_bin()
COMMAND_CODE_API_KEY = CONFIG.get("COMMAND_CODE_API_KEY", "")
BRIDGE_API_KEY = CONFIG.get("BRIDGE_API_KEY", "")
HOST = CONFIG.get("COMMANDCODE_BRIDGE_HOST", "127.0.0.1")
PORT = int(CONFIG.get("COMMANDCODE_BRIDGE_PORT", "8320"))
TIMEOUT = int(CONFIG.get("COMMANDCODE_BRIDGE_TIMEOUT", "600"))

default_workdir = os.getcwd()
WORKDIR = os.path.abspath(CONFIG.get("COMMANDCODE_BRIDGE_WORKDIR", default_workdir))


def resolve_model(model: str) -> str:
    if model in MODELS:
        return model
    lowered = model.lower()
    if lowered in ALIASES:
        return ALIASES[lowered]
    for known in MODELS:
        known_lower = known.lower()
        if lowered == known_lower or lowered.endswith("/" + known_lower) or lowered == known.rsplit("/", 1)[-1].lower():
            return known
    return model


def content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") in {"text", "input_text"}:
                    parts.append(str(item.get("text", "")))
                elif item.get("type") == "image_url":
                    parts.append(f"[image: {item.get('image_url')}]")
            else:
                parts.append(str(item))
        return "\n".join(p for p in parts if p)
    return "" if content is None else str(content)


def messages_to_prompt(messages: list[dict[str, Any]]) -> str:
    system_parts: list[str] = []
    conversation: list[str] = []
    for msg in messages:
        role = str(msg.get("role", "user"))
        text = content_to_text(msg.get("content"))
        if not text:
            continue
        if role == "system":
            system_parts.append(text)
        elif role == "assistant":
            conversation.append(f"Assistant: {text}")
        elif role == "tool":
            conversation.append(f"Tool result: {text}")
        else:
            conversation.append(f"User: {text}")
    prompt_parts: list[str] = []
    if system_parts:
        prompt_parts.append("System instructions:\n" + "\n\n".join(system_parts))
    prompt_parts.extend(conversation)
    prompt_parts.append("Assistant:")
    return "\n\n".join(prompt_parts)


def command_code_env() -> dict[str, str]:
    names = ("APPDATA", "COMSPEC", "HOMEDRIVE", "HOMEPATH", "LOCALAPPDATA", "PATH", "SYSTEMROOT", "TEMP", "TMP", "USERPROFILE")
    env = {name: os.environ[name] for name in names if name in os.environ}
    env["COMMAND_CODE_API_KEY"] = COMMAND_CODE_API_KEY
    return env


def run_command_code(model: str, prompt: str, max_turns: int = 1, keepalive_callback=None) -> str:
    if not COMMAND_CODE_API_KEY:
        raise RuntimeError("COMMAND_CODE_API_KEY is not set")
    os.makedirs(WORKDIR, exist_ok=True)
    
    # Use subprocess by default (handles stdin properly)
    # PTY only if subprocess fails due to TTY requirement
    return run_command_code_subprocess(model, prompt, max_turns, keepalive_callback)


def run_command_code_pty(model: str, prompt: str, max_turns: int = 1) -> str:
    """Run Command Code CLI with PTY (Windows with winpty)."""
    import tempfile
    env = command_code_env()
    
    # Write prompt to temp file to avoid Windows command-line length limits
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
        f.write(prompt)
        prompt_file = f.name
    
    try:
        # Create PTY
        pty = winpty.PTY(120, 40)
        
        # Build command with stdin redirection from file
        env_setup = f'set COMMAND_CODE_API_KEY={COMMAND_CODE_API_KEY}'
        cmd_args = f'{CMD_BIN} -p --model {model} --trust --skip-onboarding --max-turns {max_turns} < "{prompt_file}"'
        cmdline = f'cmd /c "{env_setup} && {cmd_args}"'
        
        # Spawn process
        pty.spawn(cmdline)
        
        # Read output with timeout
        output = ""
        start = time.time()
        last_output = start
        
        while time.time() - start < TIMEOUT:
            if not pty.isalive():
                break
            try:
                chunk = pty.read()
                if chunk:
                    output += chunk
                    last_output = time.time()
                elif time.time() - last_output > 10:
                    # No output for 10s, check if process finished
                    if not pty.isalive():
                        break
            except:
                pass
            time.sleep(0.1)
        
        # Get exit code
        exit_code = pty.get_exitstatus() if not pty.isalive() else None
        
        # Handle timeout
        if pty.isalive():
            raise RuntimeError(f"Command Code CLI timed out after {TIMEOUT}s")
        
        # Strip ANSI escape codes and terminal control sequences
        ansi_escape = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x1b]*\x1b\\|\x1b[=>]|\x1b[()][AB0]|\x1b\][0-9];[^\x07]*\x07|\x1b\[[0-9]*t')
        output = ansi_escape.sub('', output).strip()
        
        # Handle exit codes
        if exit_code == 8 and output:
            return output
        if exit_code != 0:
            detail = output or "Command Code CLI failed"
            raise RuntimeError(f"cmd exited {exit_code}: {detail}")
        
        return output
    finally:
        # Clean up temp file
        try:
            os.unlink(prompt_file)
        except:
            pass


def run_command_code_subprocess(model: str, prompt: str, max_turns: int = 1, keepalive_callback=None) -> str:
    """Run Command Code CLI with subprocess (fallback for non-Windows or no winpty)."""
    env = command_code_env()
    cmd_dir = os.path.dirname(CMD_BIN)
    if cmd_dir:
        env["PATH"] = cmd_dir + os.pathsep + env.get("PATH", "")
    elif os.name != "nt":
        env["PATH"] = "/home/deploy/.npm-global/bin:" + env.get("PATH", "")
    
    cmd = [
        CMD_BIN,
        "-p",  # non-interactive mode, reads from stdin
        "--model",
        model,
        "--trust",
        "--skip-onboarding",
        "--max-turns",
        str(max_turns),
    ]
    
    # Start the process. On Windows, suppress the console window that the
    # child would otherwise inherit/spawn (CREATE_NO_WINDOW).
    popen_kwargs: dict[str, Any] = {}
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    proc = subprocess.Popen(
        cmd,
        cwd=WORKDIR,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **popen_kwargs,
    )
    
    # Write prompt and close stdin
    proc.stdin.write(prompt)
    proc.stdin.close()
    
    # Periodic keepalive while waiting
    stop_keepalive = threading.Event()
    def keepalive_loop():
        while not stop_keepalive.wait(15):  # Send keepalive every 15 seconds
            if keepalive_callback:
                keepalive_callback()
    
    keepalive_thread = None
    if keepalive_callback:
        keepalive_thread = threading.Thread(target=keepalive_loop, daemon=True)
        keepalive_thread.start()
    
    try:
        stdout, stderr = proc.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        raise subprocess.TimeoutExpired(cmd, TIMEOUT)
    finally:
        stop_keepalive.set()
        if keepalive_thread:
            keepalive_thread.join(timeout=1)
    
    if proc.returncode == 8 and stdout.strip():
        return stdout.strip()
    if proc.returncode != 0:
        detail = (stderr or stdout or "Command Code CLI failed").strip()
        raise RuntimeError(f"cmd exited {proc.returncode}: {detail}")
    return stdout.strip()


def completion_response(model: str, content: str) -> dict[str, Any]:
    # Rough usage estimate only; Command Code CLI does not expose token usage here.
    prompt_tokens = 0
    completion_tokens = max(1, len(content) // 4)
    return {
        "id": f"chatcmpl-commandcode-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def stream_chunks(model: str, content: str) -> list[bytes]:
    base = {
        "id": f"chatcmpl-commandcode-{uuid.uuid4().hex}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
    }
    first = dict(base)
    first["choices"] = [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
    text = dict(base)
    text["choices"] = [{"index": 0, "delta": {"content": content}, "finish_reason": None}]
    last = dict(base)
    last["choices"] = [{"index": 0, "delta": {}, "finish_reason": "stop"}]
    return [
        f"data: {json.dumps(first)}\n\n".encode(),
        f"data: {json.dumps(text)}\n\n".encode(),
        f"data: {json.dumps(last)}\n\n".encode(),
        b"data: [DONE]\n\n",
    ]


class Handler(BaseHTTPRequestHandler):
    server_version = "CommandCodeBridge/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}", flush=True)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _safe_error(self, status: int, message: str, errtype: str) -> None:
        """Send an error response, silently dropping it if the client is gone."""
        try:
            self._send_json(status, {"error": {"message": message, "type": errtype}})
        except OSError:
            self.close_connection = True

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode() or "{}")

    def _authorized(self) -> bool:
        if not BRIDGE_API_KEY:
            return True
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {BRIDGE_API_KEY}"

    def do_GET(self) -> None:
        if self.path.rstrip("/") in {"/health", "/v1/health"}:
            self._send_json(200, {"ok": True})
            return
        if self.path.rstrip("/") == "/v1/models":
            if not self._authorized():
                self._send_json(401, {"error": {"message": "Unauthorized", "type": "auth_error"}})
                return
            self._send_json(200, {
                "object": "list",
                "data": [
                    {"id": m, "object": "model", "created": 1781650223, "owned_by": "Command Code CLI"}
                    for m in MODELS
                ],
            })
            return
        self._send_json(404, {"error": {"message": "Not found", "type": "not_found"}})

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/v1/chat/completions":
            self._send_json(404, {"error": {"message": "Not found", "type": "not_found"}})
            return
        if not self._authorized():
            self._send_json(401, {"error": {"message": "Unauthorized", "type": "auth_error"}})
            return
        try:
            req = self._read_json()
            model = resolve_model(str(req.get("model", MODELS[0])))
            messages = req.get("messages") or []
            if not isinstance(messages, list):
                raise ValueError("messages must be an array")
            prompt = messages_to_prompt(messages)
            max_turns = int(req.get("max_turns") or CONFIG.get("COMMANDCODE_BRIDGE_MAX_TURNS", "10"))
            
            # For streaming, send headers early and use keepalive.
            # Body is EOF-delimited (HTTP/1.0 + Connection: close): never set
            # Transfer-Encoding: chunked, since http.server does not chunk
            # frames automatically and clients abort on the mismatch.
            if req.get("stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()

                # Keepalive callback sends SSE comment lines (ignored by parsers)
                # so client-side read timeouts don't fire during long runs.
                def send_keepalive() -> None:
                    try:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
                    except OSError:
                        pass

                # Run CLI with keepalive
                content = run_command_code(model, prompt, max_turns=max_turns, keepalive_callback=send_keepalive)

                # Send actual content chunks; client disconnect is normal here.
                for chunk in stream_chunks(model, content):
                    self.wfile.write(chunk)
                    self.wfile.flush()
                self.close_connection = True
            else:
                # Non-streaming: just run normally
                content = run_command_code(model, prompt, max_turns=max_turns)
                self._send_json(200, completion_response(model, content))
        except ConnectionError:
            # Client closed the socket mid-response; nothing to send back.
            self.close_connection = True
        except subprocess.TimeoutExpired:
            self._safe_error(504, "Command Code CLI timed out", "timeout_error")
        except Exception as exc:
            self._safe_error(500, str(exc), "bridge_error")


def main() -> None:
    if not COMMAND_CODE_API_KEY:
        raise SystemExit("COMMAND_CODE_API_KEY is required")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"CommandCode bridge listening on {HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
