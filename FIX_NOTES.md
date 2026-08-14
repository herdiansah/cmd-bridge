# CommandCode Bridge Fix - PTY Solution

## Problem
Command Code CLI v1.4.1 introduced a breaking change that requires a TTY (interactive terminal) for all operations, including the `-p` (print) mode. The bridge's `subprocess.run()` with `input=prompt` approach was rejected with:

```
Error: Interactive mode requires a TTY terminal.
Please run this command directly in your terminal, not through a pipe or redirect.
```

## Solution
Implemented PTY (pseudo-terminal) support using the `pywinpty` library on Windows:

1. **Install pywinpty**: `pip install pywinpty`
2. **Modified bridge.py**:
   - Added conditional PTY support with fallback to subprocess
   - Created `run_command_code_pty()` function that allocates a pseudo-TTY
   - Passes prompt as `-p` argument instead of stdin
   - Strips ANSI escape codes from PTY output using regex
   - Maintains backward compatibility for non-Windows systems

## Key Changes
- Import `winpty` with fallback detection
- Use `winpty.PTY(120, 40)` to create pseudo-terminal
- Build command: `cmd /c "set API_KEY=... && command-code.cmd -p \"prompt\" ..."`
- Read PTY output with timeout and alive checks
- Strip ANSI codes: `\x1b\[[0-9;?]*[a-zA-Z]` and related sequences

## Testing
✅ `/v1/models` endpoint working
✅ `/v1/chat/completions` with simple prompts working
✅ Clean output without ANSI escape codes
✅ Response times: 19-30 seconds (acceptable for CLI delegation)

## Files Modified
- `bridge.py`: Added PTY support with ANSI stripping

## Dependencies
- `pywinpty==3.0.5` (Windows only)
- Existing dependencies unchanged
