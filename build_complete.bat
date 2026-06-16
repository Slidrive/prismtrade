@echo off
echo ========================================
echo PRISMTRADE - Complete Build Process
echo ========================================
echo.

cd /d "%~dp0"

REM Step 1: Build Frontend
echo [1/3] Building React frontend...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

call npm run build
if errorlevel 1 (
    echo ERROR: npm build failed
    pause
    exit /b 1
)

cd ..

REM Step 2: Test locally
echo.
echo [2/3] Frontend built successfully!
echo.
echo Testing API endpoints...
python -c "from app import app; print('Flask app imports OK')"
if errorlevel 1 (
    echo ERROR: Flask app has import errors
    pause
    exit /b 1
)

echo.
echo [3/3] Ready for deployment!
echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo 1. Test locally: python app.py
echo 2. Deploy to Railway: .\deploy_to_railway.bat
echo ========================================
echo.
pause
