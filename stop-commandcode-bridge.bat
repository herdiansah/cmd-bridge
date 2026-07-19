@echo off
setlocal

powershell.exe -NoProfile -Command "$bridge = Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Where-Object { $_.CommandLine -match '(^|\s)bridge\.py(\s|$)' }; if ($null -eq $bridge) { Write-Host 'CommandCode Bridge is not running.'; exit 0 }; $bridge | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('Stopped CommandCode Bridge (PID ' + $_.ProcessId + ').') }"
exit /b %ERRORLEVEL%
