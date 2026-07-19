@echo off
setlocal

if "%COMMAND_CODE_API_KEY%"=="" (
  echo COMMAND_CODE_API_KEY is required.
  exit /b 1
)

python "%~dp0bridge.py"
