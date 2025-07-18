@echo off
REM Set a clean temporary folder for LibreTranslate to store its DB
set "DB_FOLDER=%TEMP%\LibreTranslate"
mkdir "%DB_FOLDER%" >nul 2>&1

REM Change working directory to that folder
cd /d "%DB_FOLDER%"
if errorlevel 1 (
    echo [ERROR] Failed to change directory to: "%DB_FOLDER%"
    pause
    exit /b 2
)

REM Start LibreTranslate with full debug logs visible in the terminal
echo [INFO] Starting LibreTranslate
libretranslate --host 0.0.0.0 --port 8081 --debug

pause
