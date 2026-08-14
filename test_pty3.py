#!/usr/bin/env python3
"""Test Command Code CLI with PTY using winpty."""

import os
import sys
import time
import winpty

# Set API key
os.environ["COMMAND_CODE_API_KEY"] = "user_MyLK6yj3P23fqxNd347trZyqVbK6Qk8VQT9f8tSmfwYPFoMuMTiAK5JFAVMkgNQq4viGaMNZkVnhSyyDweJ9jXg"

cmd_bin = r"C:\Users\PC\AppData\Roaming\npm\command-code.cmd"
prompt = "What is 2+2? Answer in one word."

# Create PTY process
print("Creating PTY...")
pty = winpty.PTY(80, 24)

# Spawn command
cmdline = f'cmd /c "set COMMAND_CODE_API_KEY={os.environ["COMMAND_CODE_API_KEY"]} && {cmd_bin} --model deepseek/deepseek-v4-pro --trust --skip-onboarding --max-turns 1 -p"'
print(f"Spawning command...")
pty.spawn(cmdline)

# Wait for process to start
time.sleep(2)

# Write prompt
print(f"Writing prompt: {prompt}")
pty.write(prompt + "\n")

# Read output with timeout
output = ""
start = time.time()
timeout_sec = 90

print("Reading output...")
try:
    while time.time() - start < timeout_sec:
        if not pty.isalive():
            print("\nProcess exited")
            break
        try:
            chunk = pty.read()
            if chunk:
                output += chunk
                print(chunk, end="", flush=True)
        except:
            pass
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nInterrupted")
except Exception as e:
    print(f"\nRead error: {e}", file=sys.stderr)

print(f"\n\n=== Exit code: {pty.get_exitstatus() if not pty.isalive() else 'still running'} ===")
print(f"=== Full output ({len(output)} chars) ===")
if output:
    print(output)
else:
    print("(no output)")
