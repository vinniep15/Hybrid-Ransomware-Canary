@echo off
:: ====================================================
:: AUTHOR: Vincent Priestley
:: PROJECT: Hybrid Ransomware Canary V1.6
:: DESCRIPTION: Fixed Pathing for Windows Terminal
:: ====================================================
TITLE Canary Orchestrator - VP Edition
color 0B

:: I'm getting the directory where this script is actually running
set "PROJECT_PATH=%~dp0"
:: Removing the trailing backslash if it exists for cleaner pathing
if "%PROJECT_PATH:~-1%"=="\" set "PROJECT_PATH=%PROJECT_PATH:~0,-1%"

echo [*] Initialising Security Environment for Vincent Priestley...

:: I'm launching the backend and sensor using a much more stable syntax.
:: I've replaced the messy nested quotes with a direct call.
start /min wt -w 0 nt -p "Command Prompt" --title "Canary BACKEND" cmd /k "cd /d %PROJECT_PATH% && python scripts/backend.py" ; sp -p "Command Prompt" --title "Canary SENSOR" cmd /k "cd /d %PROJECT_PATH% && python scripts/sensor.py"

timeout /t 5 /nobreak > nul
start http://localhost:8000
exit