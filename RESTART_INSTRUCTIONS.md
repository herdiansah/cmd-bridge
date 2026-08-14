# CommandCode Bridge - OMP Integration Status

## ✅ Configuration Complete

**Date**: 2026-08-06  
**Config File**: `%APPDATA%\orca\codex-runtime-home\home\config.toml`

### Current Status

✅ **Provider Added**: `commandcode-bridge`
- Base URL: http://127.0.0.1:8320/v1
- Wire API: responses
- No auth required

✅ **Bridge Running**: Listening on port 8320

✅ **4 Models Configured**:
1. `cmdcode/deepseek-v4-pro` - DeepSeek V4 Pro (CommandCode)
2. `cmdcode/nemotron-3-ultra` - Nemotron 3 Ultra 550B (CommandCode)
3. `cmdcode/minimax-m3` - MiniMax M3 (CommandCode)
4. `cmdcode/mimo-v2.5-pro` - Xiaomi Mimo V2.5 Pro (CommandCode)

### Next Step: Restart OMP/Orca

**Important**: You must restart Orca/OMP completely for the models to appear:

1. **Close Orca** completely (not just minimize)
2. **Reopen Orca**
3. Open model picker in Codex/Claude interface
4. Look for models starting with `cmdcode/`

### Verification

After restart, the models should appear as:
- DeepSeek V4 Pro (CommandCode)
- Nemotron 3 Ultra 550B (CommandCode)
- MiniMax M3 (CommandCode)
- Xiaomi Mimo V2.5 Pro (CommandCode)

### Troubleshooting

**If models still don't appear**:
1. Check config syntax: `type "$APPDATA\orca\codex-runtime-home\home\config.toml" | grep -A 20 commandcode-bridge`
2. Verify bridge is running: `curl http://127.0.0.1:8320/v1/models`
3. Check OMP logs for errors
4. Verify no TOML syntax errors in config file

**Note**: OMP may rewrite config.toml on restart. If the configuration disappears again, it might need to be added through OMP's UI or API instead of direct file editing.

### Alternative: Use Direct HTTP Calls

If OMP integration continues to have issues, you can use the bridge directly via HTTP:

```bash
curl -X POST http://127.0.0.1:8320/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek/deepseek-v4-pro","messages":[{"role":"user","content":"Your prompt here"}]}'
```

Or integrate with other OpenAI-compatible clients pointing to `http://127.0.0.1:8320/v1`
