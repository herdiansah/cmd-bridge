# CommandCode Bridge - Oh My Pi Configuration Update

## ✅ Configuration Added to Correct Location

**Date**: 2026-08-06  
**Config File**: Codex Account Config  
**Path**: `%APPDATA%\orca\codex-accounts\0890dc0f-7de8-45d1-b5ce-86ee326743b7\home\config.toml`

### What Was Added

✅ **Provider Section**:
```toml
[model_providers.commandcode-bridge]
name = "CommandCode Bridge (Local)"
base_url = "http://127.0.0.1:8320/v1"
env_key = ""
wire_api = "responses"
stream_idle_timeout_ms = 300000
```

✅ **4 Model Definitions**:
1. `cmdcode/deepseek-v4-pro` - DeepSeek V4 Pro (CommandCode)
2. `cmdcode/nemotron-3-ultra` - Nemotron 3 Ultra 550B (CommandCode)
3. `cmdcode/minimax-m3` - MiniMax M3 (CommandCode)
4. `cmdcode/mimo-v2.5-pro` - Xiaomi Mimo V2.5 Pro (CommandCode)

### Important Notes

**Configuration was added to BOTH locations**:
1. ✅ Codex Runtime Home: `codex-runtime-home/home/config.toml`
2. ✅ Codex Account Config: `codex-accounts/0890dc0f-.../home/config.toml`

**Backups created**:
- `config.toml.backup` in both locations

### Next Steps

1. **Close Oh My Pi/Orca completely**
2. **Restart Orca**
3. **Open Codex interface**
4. **Click model picker** (top of interface)
5. **Look for CommandCode Bridge models**

### What to Look For

In the Codex model picker, you should see:
- "DeepSeek V4 Pro (CommandCode)"
- "Nemotron 3 Ultra 550B (CommandCode)"
- "MiniMax M3 (CommandCode)"
- "Xiaomi Mimo V2.5 Pro (CommandCode)"

Or check for a provider section labeled "CommandCode Bridge (Local)"

### If Models Don't Appear

1. Check that bridge is running: `netstat -an | grep ":8320"`
2. Verify config wasn't overwritten: `tail "$APPDATA\orca\codex-accounts\0890dc0f-7de8-45d1-b5ce-86ee326743b7\home\config.toml"`
3. Check Orca logs for TOML parsing errors
4. Verify the correct Codex account is active in Orca

### Bridge Status

- ✅ Bridge running on http://127.0.0.1:8320
- ✅ All 4 models verified working
- ✅ PTY implementation with ANSI stripping
- ✅ Ready to use
