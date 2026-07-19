@echo off
setlocal

curl.exe --silent --fail http://127.0.0.1:8320/health >nul 2>&1
if not errorlevel 1 (
  echo CommandCode Bridge is already running at http://127.0.0.1:8320
  exit /b 0
)

if "%COMMAND_CODE_API_KEY%"=="" (
  set /p "COMMAND_CODE_API_KEY=Enter your Command Code API key: "
)

if "%COMMAND_CODE_API_KEY%"=="" (
  echo COMMAND_CODE_API_KEY is required.
  exit /b 1
)

python "%~dp0bridge.py"
