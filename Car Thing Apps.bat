@echo off
setlocal
cd /d "%~dp0"

where pythonw >nul 2>nul
if %errorlevel% equ 0 (
  start "Car Thing Apps" pythonw "%~dp0carthing_apps.py"
  exit /b 0
)

where python >nul 2>nul
if %errorlevel% equ 0 (
  start "Car Thing Apps" python "%~dp0carthing_apps.py"
  exit /b 0
)

for %%P in (
  "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
  "%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe"
  "%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe"
  "C:\Program Files\Python312\pythonw.exe"
  "C:\Program Files\Python311\pythonw.exe"
  "C:\Program Files\Python310\pythonw.exe"
) do (
  if exist "%%~P" (
    start "Car Thing Apps" "%%~P" "%~dp0carthing_apps.py"
    exit /b 0
  )
)

python "%~dp0carthing_apps.py"
if errorlevel 1 pause
