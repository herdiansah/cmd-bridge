#!/usr/bin/env python3
"""OpenAI-compatible bridge for Command Code CLI models.

This exposes /v1/models and /v1/chat/completions, then delegates each request to
`cmd -p --model ...`. It is intentionally simple because Command Code's Go-plan
Provider API returns 403, while the CLI itself can use the included open-model
credits.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

MODELS = [
    "deepseek/deepseek-v4-pro",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "MiniMaxAI/MiniMax-M3",
    "xiaomi/mimo-v2.5-pro",
]

ALIASES = {
    "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
    "nemotron-3-ultra": "nvidia/nemotron-3-ultra-550b-a55b",
    "nemotron-3-ultra-550b-a55b": "nvidia/nemotron-3-ultra-550b-a55b",
    "minimax-m3": "MiniMaxAI/MiniMax-M3",
    "mimo-v2.5-pro": "xiaomi/mimo-v2.5-pro",
}

def resolve_cmd_bin() -> str:
    env_bin = os.environ.get("COMMAND_CODE_BIN")
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
COMMAND_CODE_API_KEY = os.environ.get("COMMAND_CODE_API_KEY", "")
BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY", "")
HOST = os.environ.get("COMMANDCODE_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("COMMANDCODE_BRIDGE_PORT", "8320"))
TIMEOUT = int(os.environ.get("COMMANDCODE_BRIDGE_TIMEOUT", "600"))

default_workdir = os.path.join(tempfile.gettempdir(), "commandcode-bridge-workdir")
WORKDIR = os.environ.get("COMMANDCODE_BRIDGE_WORKDIR", default_workdir)


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


def run_command_code(model: str, prompt: str, max_turns: int = 1) -> str:
    if not COMMAND_CODE_API_KEY:
        raise RuntimeError("COMMAND_CODE_API_KEY is not set")
    os.makedirs(WORKDIR, exist_ok=True)
    env = os.environ.copy()
    env["COMMAND_CODE_API_KEY"] = COMMAND_CODE_API_KEY
    cmd_dir = os.path.dirname(CMD_BIN)
    if cmd_dir:
        env["PATH"] = cmd_dir + os.pathsep + env.get("PATH", "")
    else:
        if os.name != "nt":
            env["PATH"] = "/home/deploy/.npm-global/bin:" + env.get("PATH", "")
    # Pass the prompt over stdin instead of argv. Gateway conversations can be
    # large enough to exceed the OS argument-size limit when forwarded as
    # `cmd -p <prompt>`.
    cmd = [
        CMD_BIN,
        "-p",
        "--model",
        model,
        "--trust",
        "--skip-onboarding",
        "--max-turns",
        str(max_turns),
    ]
    proc = subprocess.run(
        cmd,
        cwd=WORKDIR,
        env=env,
        input=prompt,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=TIMEOUT,
    )
    # Command Code exits with 8 when --max-turns is reached. In bridge mode that
    # should not poison CLIProxy auth if the CLI still produced useful text.
    if proc.returncode == 8 and proc.stdout.strip():
        return proc.stdout.strip()
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "Command Code CLI failed").strip()
        raise RuntimeError(f"cmd exited {proc.returncode}: {detail}")
    return proc.stdout.strip()


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
            max_turns = int(req.get("max_turns") or os.environ.get("COMMANDCODE_BRIDGE_MAX_TURNS", "3"))
            content = run_command_code(model, prompt, max_turns=max_turns)
            if req.get("stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                for chunk in stream_chunks(model, content):
                    self.wfile.write(chunk)
                    self.wfile.flush()
                self.close_connection = True
            else:
                self._send_json(200, completion_response(model, content))
        except subprocess.TimeoutExpired:
            self._send_json(504, {"error": {"message": "Command Code CLI timed out", "type": "timeout_error"}})
        except Exception as exc:
            self._send_json(500, {"error": {"message": str(exc), "type": "bridge_error"}})


def main() -> None:
    if not COMMAND_CODE_API_KEY:
        raise SystemExit("COMMAND_CODE_API_KEY is required")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"CommandCode bridge listening on {HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
