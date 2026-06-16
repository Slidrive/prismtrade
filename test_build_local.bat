@echo off
echo ========================================
echo PrismTrade Local Build Test
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

echo [2/3] Building React frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: npm build failed
    pause
    exit /b 1
)

cd ..

echo [3/3] Starting Flask server...
echo.
echo Frontend built successfully!
echo Starting server at http://localhost:5000
echo.
python app.py

pause
