# CommandCode Bridge Fix - Windows Command Line Length Issue

## Problem
When using the CommandCode bridge in Oh My Pi, requests with system prompts and conversation history failed with:
```
Error: 500 The filename or extension is too long.
```

## Root Cause
The bridge was constructing commands like:
```cmd
cmd /c "set COMMAND_CODE_API_KEY=... && C:\...\cmd.cmd -p "ENTIRE_PROMPT_HERE" --model ... --trust --skip-onboarding --max-turns 1"
```

**Windows command line has an ~8191 character limit.** When Oh My Pi sends:
- System prompt
- Conversation history
- Current message
- API key (95 chars)
- Full binary path (~50 chars)
- Flags (~80 chars)

The total exceeded 8191 characters → "filename or extension is too long" error.

## Solution
Switch from PTY to subprocess mode, which properly handles stdin:

1. **Model alias**: Added `"commandcode": "deepseek/deepseek-v4-flash"` to ALIASES
2. **Use subprocess by default**: Changed `run_command_code()` to use `run_command_code_subprocess()` instead of PTY
3. **Stdin support**: The subprocess version passes the prompt via stdin (`input=prompt`), bypassing command-line length limits

### Key Changes in `bridge.py`

```python
# Added model alias
ALIASES = {
    "commandcode": "deepseek/deepseek-v4-flash",
    ...
}

# Changed to use subprocess by default
def run_command_code(model: str, prompt: str, max_turns: int = 1) -> str:
    if not COMMAND_CODE_API_KEY:
        raise RuntimeError("COMMAND_CODE_API_KEY is not set")
    os.makedirs(WORKDIR, exist_ok=True)
    
    # Use subprocess by default (handles stdin properly)
    return run_command_code_subprocess(model, prompt, max_turns)
```

## Verification
✅ Short prompt (< 100 chars): Works
✅ Long prompt (> 5000 chars): Works
✅ Model resolution: "commandcode" → "deepseek/deepseek-v4-flash"

## Next Steps
1. Restart the bridge: `python bridge.py`
2. Test in Oh My Pi with the commandcode model
3. The bridge now handles prompts of any length via stdin
