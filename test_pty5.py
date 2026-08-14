#!/usr/bin/env python3
"""Test Command Code CLI with PTY using winpty."""

import os
import sys
import time
import winpty

# Set API key
os.environ["COMMAND_CODE_API_KEY"] = "user_MyLK6yj3P23fqxNd347trZyqVbK6Qk8VQT9f8tSmfwYPFoMuMTiAK5JFAVMkgNQq4viGaMNZkVnhSyyDweJ9jXg"

cmd_bin = r"C:\Users\PC\AppData\Roaming\npm\command-code.cmd"
prompt = "What is 2+2?"

# Create PTY process
print("Creating PTY...")
pty = winpty.PTY(120, 40)

# Spawn command - use proper escaping
env_setup = f'set COMMAND_CODE_API_KEY={os.environ["COMMAND_CODE_API_KEY"]}'
cmd_args = f'{cmd_bin} -p "{prompt}" --model deepseek/deepseek-v4-pro --trust --skip-onboarding --max-turns 1'
cmdline = f'cmd /c "{env_setup} && {cmd_args}"'

print(f"Command: {cmd_args}")
pty.spawn(cmdline)

# Read output with timeout
output = ""
start = time.time()
timeout_sec = 90
last_output = start

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
                last_output = time.time()
            elif time.time() - last_output > 10:  # 10s no output
                print("\nNo output for 10s, checking if alive...")
                if not pty.isalive():
                    break
        except:
            pass
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nInterrupted")
except Exception as e:
    print(f"\nError: {e}", file=sys.stderr)

exit_code = pty.get_exitstatus() if not pty.isalive() else None
print(f"\n\n=== Exit code: {exit_code} ===")
print(f"=== Output length: {len(output)} chars ===")
if output:
    print(output)
