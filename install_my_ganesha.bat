@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
  )
)

if not defined PYTHON_CMD (
  where python3 >nul 2>nul
  if not errorlevel 1 (
    python3 -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python3"
  )
)

if not defined PYTHON_CMD goto :python_missing

set "VENV_NEEDS_REBUILD="
if exist ".venv" (
  if not exist ".venv\pyvenv.cfg" set "VENV_NEEDS_REBUILD=1"
  if not exist ".venv\Scripts\python.exe" set "VENV_NEEDS_REBUILD=1"
  if not exist ".venv\Scripts\pythonw.exe" set "VENV_NEEDS_REBUILD=1"
)
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys" >nul 2>nul
  if errorlevel 1 set "VENV_NEEDS_REBUILD=1"
)

if defined VENV_NEEDS_REBUILD (
  echo.
  echo The existing private Python environment is incomplete and will be rebuilt.
  rmdir /s /q ".venv"
  if exist ".venv" goto :install_failed
)

if not exist ".venv\Scripts\pythonw.exe" %PYTHON_CMD% -m venv .venv
if errorlevel 1 goto :install_failed

call ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :install_failed

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0startup.ps1" -Install
if errorlevel 1 goto :install_failed

start "" ".venv\Scripts\pythonw.exe" "app.py"
echo.
echo My Ganesha is installed, running, and configured to start with Windows.
echo Left-click him to wave. Right-click him to exit.
pause
exit /b 0

:python_missing
echo.
echo Python 3.10 or newer was not found.
echo.
where winget >nul 2>nul
if errorlevel 1 goto :manual_python

choice /C YN /N /M "Install Python automatically now using Windows Package Manager? [Y/N]: "
if errorlevel 2 goto :manual_python

winget install --id Python.Python.3.12 --exact --source winget --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto :manual_python

echo.
echo Python was installed successfully.
echo Please CLOSE this window, then double-click install_my_ganesha.bat again.
pause
exit /b 0

:manual_python
echo.
echo Please install Python 3 from:
echo https://www.python.org/downloads/windows/
echo.
echo IMPORTANT: select "Add python.exe to PATH" during installation.
echo Then close this window and run install_my_ganesha.bat again.
pause
exit /b 1

:install_failed
echo.
echo My Ganesha installation did not complete.
echo Please keep this window open and share the error lines shown above with me.
pause
exit /b 1
