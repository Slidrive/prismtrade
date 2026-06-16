@echo off
cls
echo ================================================================
echo PRISM TRADE - PHASE 1 COMPLETE DEPLOYMENT
echo ================================================================
echo.
echo NEW FEATURES ADDED:
echo  [+] API Keys Management Page
echo  [+] Live Trading Interface
echo  [+] Real-time Price Display
echo  [+] Position Management
echo  [+] Trade History
echo.
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/3] Building frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
cd ..

echo.
echo [2/3] Committing to git...
git add .
git commit -m "Phase 1 Complete: Added API Keys, Live Trading, Positions, Trade History"

echo.
echo [3/3] Deploying to Railway...
git push origin main --force

if errorlevel 1 (
    echo.
    echo WARNING: Git push failed
    pause
    exit /b 1
)

echo.
echo ================================================================
echo DEPLOYMENT COMPLETE!
echo ================================================================
echo.
echo Railway is deploying now (2-3 minutes)
echo.
echo Visit: https://prismtrade-production.up.railway.app
echo.
echo NEW PAGES:
echo  - /api-keys   (Store your Gemini API keys)
echo  - /trading    (Live buy/sell interface)
echo.
echo ================================================================
pause
