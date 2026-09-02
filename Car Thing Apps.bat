@echo off
cd /d "%~dp0"
set PY=C:\Users\Gilzh\AppData\Local\Programs\Python\Python312\pythonw.exe
if exist "%PY%" (
  start "Car Thing Apps" "%PY%" "%~dp0carthing_apps.py"
  exit /b 0
)
set PY=C:\Users\Gilzh\AppData\Local\Programs\Python\Python312\python.exe
if exist "%PY%" (
  start "Car Thing Apps" "%PY%" "%~dp0carthing_apps.py"
  exit /b 0
)
python "%~dp0carthing_apps.py"
if errorlevel 1 pause
