#!/usr/bin/env python3
"""Test Command Code CLI with PTY using pywinpty."""

import os
import sys
import winpty

# Set API key
os.environ["COMMAND_CODE_API_KEY"] = "user_MyLK6yj3P23fqxNd347trZyqVbK6Qk8VQT9f8tSmfwYPFoMuMTiAK5JFAVMkgNQq4viGaMNZkVnhSyyDweJ9jXg"

cmd_bin = r"C:\Users\PC\AppData\Roaming\npm\command-code.cmd"
prompt = "What is 2+2? Answer in one word.\n"

# Create PTY process
pty = winpty.PTY(80, 24)

# Spawn command
cmdline = f'"{cmd_bin}" --model deepseek/deepseek-v4-pro --trust --skip-onboarding --max-turns 1 -p'
pty.spawn(cmdline)

# Write prompt
pty.write(prompt)

# Read output
output = ""
try:
    while True:
        chunk = pty.read()
        if not chunk:
            break
        output += chunk
        print(chunk, end="", flush=True)
except Exception as e:
    print(f"\nRead error: {e}", file=sys.stderr)

print(f"\n\n=== Full output ===\n{output}")
