@echo off
cd /d "%~dp0"
if not exist ".venv\pyvenv.cfg" goto :repair_required
if not exist ".venv\Scripts\python.exe" goto :repair_required
if not exist ".venv\Scripts\pythonw.exe" goto :repair_required

".venv\Scripts\python.exe" -c "import sys" >nul 2>nul
if errorlevel 1 goto :repair_required

start "" ".venv\Scripts\pythonw.exe" "app.py"
exit /b 0

:repair_required
echo.
echo My Ganesha's private Python environment is missing or incomplete.
echo Please run install_my_ganesha.bat to repair it automatically.
echo.
pause
exit /b 1
