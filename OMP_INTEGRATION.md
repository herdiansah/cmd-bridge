# CommandCode Bridge - Oh My Pi Integration

## Configuration Complete ✅

Successfully added CommandCode Bridge as a custom provider to Oh My Pi (Codex runtime).

### Provider Configuration
- **Name**: CommandCode Bridge (Local)
- **Base URL**: http://127.0.0.1:8320/v1
- **Wire API**: responses
- **Location**: `%APPDATA%\orca\codex-runtime-home\home\config.toml`

### Verified Working Models

All 4 models were tested and verified working:

1. **cmdcode/deepseek-v4-pro** - DeepSeek V4 Pro
   - ✅ Tested with math and factual queries
   - Response time: ~22-26s

2. **cmdcode/nemotron-3-ultra** - Nvidia Nemotron 3 Ultra 550B
   - ✅ Tested successfully
   - Response time: ~26s

3. **cmdcode/minimax-m3** - MiniMax M3
   - ✅ Tested with math queries
   - Response time: ~22-27s

4. **cmdcode/mimo-v2.5-pro** - Xiaomi Mimo V2.5 Pro
   - ✅ Tested and responded correctly
   - Response time: ~14-15s (fastest)

### Model Slugs in OMP
```
cmdcode/deepseek-v4-pro
cmdcode/nemotron-3-ultra
cmdcode/minimax-m3
cmdcode/mimo-v2.5-pro
```

### Usage
1. **Start the bridge**: `python bridge.py`
2. **Use in OMP**: Select any of the `cmdcode/*` models from the model picker
3. Models will appear in Codex/Claude interfaces after OMP restart

### Notes
- Bridge must be running at http://127.0.0.1:8320 for models to work
- Uses PTY (pywinpty) to satisfy Command Code CLI 1.4.1 TTY requirement
- ANSI escape codes are automatically stripped from responses
- No API key required for bridge endpoint (Command Code API key used internally)

### Backup
Original config backed up to:
`%APPDATA%\orca\codex-runtime-home\home\config.toml.backup`

### Next Steps
Restart OMP/Orca to load the new provider and models.
