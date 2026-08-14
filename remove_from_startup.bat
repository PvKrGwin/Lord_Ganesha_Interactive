@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0startup.ps1" -Remove
echo My Ganesha will no longer start automatically. The app files were not deleted.
pause
