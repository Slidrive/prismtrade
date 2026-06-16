@echo off
cls
echo ================================================================
echo PRISM TRADE - TEST LOCALLY BEFORE DEPLOYING
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/2] Rebuilding frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
cd ..

echo.
echo [2/2] Starting Flask server...
echo.
echo ================================================================
echo SERVER STARTING
echo ================================================================
echo.
echo Visit: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo ================================================================
echo.

python app.py
