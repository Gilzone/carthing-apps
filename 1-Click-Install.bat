@echo off
setlocal enabledelayedexpansion
title Spotify Car Thing — 1-Click Installer
cd /d "%~dp0"

echo ========================================================================
echo    Spotify Car Thing — 1-Click Complete Installer
echo ========================================================================
echo.

:: 1. Locate Python
set "PY_CMD="

where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :RUN_INSTALL
)

where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :RUN_INSTALL
)

for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
) do (
    if exist "%%~P" (
        set "PY_CMD=%%~P"
        goto :RUN_INSTALL
    )
)

echo [!] Python was not detected in PATH.
echo Attempting to install Python via Windows Package Manager (winget)...
echo.
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if %errorlevel% equ 0 (
    echo.
    echo [!] Python installed successfully. Restarting installer...
    timeout /t 3 >nul
    call "%~f0"
    exit /b 0
)

echo.
echo [X] Could not install Python automatically.
echo Please install Python 3 from https://www.python.org/downloads/
echo (Make sure to check "Add Python to PATH" during installation)
echo.
pause
exit /b 1

:RUN_INSTALL
"%PY_CMD%" "%~dp0install.py" %*
if %errorlevel% neq 0 (
    echo.
    echo [!] Installation encountered an issue. See above for details.
    pause
    exit /b %errorlevel%
)

echo.
echo Press any key to exit...
pause >nul
exit /b 0
