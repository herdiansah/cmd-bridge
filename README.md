# CommandCode Bridge

OpenAI-compatible local gateway for the Command Code CLI. It exposes Command Code models to 9router on Windows.

## Prerequisites

- Python 3.11+
- Node.js and npm
- Command Code installed globally:

  ```powershell
  npm install --global command-code
  ```

- 9router installed globally:

  ```powershell
  npm install --global 9router
  ```

## Configure the Command Code key

Set the key for the current PowerShell session:

```powershell
$env:COMMAND_CODE_API_KEY = "your-commandcode-key"
```

To persist it for future terminals, use:

```powershell
[Environment]::SetEnvironmentVariable(
  "COMMAND_CODE_API_KEY",
  "your-commandcode-key",
  "User"
)
```

Open a new terminal after setting a persistent user environment variable.

## Start the bridge

The bridge is not installed as a Windows startup task. Run this batch file after sign-in:

```powershell
.\start-commandcode-bridge.bat
```

It exits successfully when the bridge is already healthy; otherwise it prompts for an unset API key and runs the bridge in that terminal. Keep that terminal open while using the bridge.

`start-bridge.cmd` is an equivalent non-interactive launcher for sessions where `COMMAND_CODE_API_KEY` is already set.

## Stop the bridge

For a bridge started with `start-commandcode-bridge.bat`, run:

```powershell
.\stop-commandcode-bridge.bat
```

If managed through PM2, stop it through PM2 instead:

```powershell
pm2 stop commandcode-bridge
```

The bridge listens only on `127.0.0.1:8320` and provides:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`

Example direct request:

```powershell
curl.exe http://127.0.0.1:8320/v1/models

curl.exe -X POST http://127.0.0.1:8320/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"model":"deepseek/deepseek-v4-pro","messages":[{"role":"user","content":"What is 2+2?"}]}'
```

## Register with 9router

With the bridge running and `COMMAND_CODE_API_KEY` set:

```powershell
python .\register_bridge.py
```

Restart 9router after registration:

```powershell
9router -n
```

The registration creates the OpenAI-compatible provider at `http://127.0.0.1:8320/v1` with the alias `cmdcode`.

### Available 9router model IDs

- `cmdcode/deepseek/deepseek-v4-pro`
- `cmdcode/nvidia/nemotron-3-ultra-550b-a55b`
- `cmdcode/MiniMaxAI/MiniMax-M3`
- `cmdcode/xiaomi/mimo-v2.5-pro`

Use 9router's OpenAI-compatible endpoint:

```text
http://127.0.0.1:20128/v1
```

Example end-to-end request:

```powershell
curl.exe -X POST http://127.0.0.1:20128/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"model":"cmdcode/deepseek/deepseek-v4-pro","stream":false,"messages":[{"role":"user","content":"What is 2+2?"}]}'
```

## PM2 option

If PM2 is installed, the included `ecosystem.config.cjs` provides auto-restart:

```powershell
npm install --global pm2
pm2 start .\ecosystem.config.cjs
pm2 save
```

The PM2 configuration reads `COMMAND_CODE_API_KEY` from the process environment; it does not store credentials in the repository.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `COMMAND_CODE_API_KEY` | Required | Command Code API key. |
| `COMMAND_CODE_BIN` | Auto-detected | Explicit Command Code executable path. On Windows, use the npm shim such as `%APPDATA%\npm\command-code.cmd`. |
| `COMMANDCODE_BRIDGE_HOST` | `127.0.0.1` | Bridge bind address. |
| `COMMANDCODE_BRIDGE_PORT` | `8320` | Bridge port. |
| `COMMANDCODE_BRIDGE_TIMEOUT` | `600` | Command Code CLI timeout in seconds. |
| `COMMANDCODE_BRIDGE_WORKDIR` | System temp directory | CLI working directory. |
| `BRIDGE_API_KEY` | Unset | Optional bearer token required by the bridge API. |

If `BRIDGE_API_KEY` is set, send it to the bridge as:

```text
Authorization: Bearer <BRIDGE_API_KEY>
```
