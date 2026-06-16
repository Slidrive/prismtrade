@echo off
cls
echo ================================================================
echo PRISM TRADE - RAPID REBUILD ^& DEPLOY
echo ================================================================
echo.
echo [STEP 1] Rebuilding frontend with PRISM TRADE branding...
echo.

cd /d "%~dp0"
cd frontend

echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: npm install failed!
    pause
    exit /b 1
)

echo.
echo Building production bundle...
call npm run build
if errorlevel 1 (
    echo.
    echo ERROR: npm build failed!
    pause
    exit /b 1
)

cd ..

echo.
echo ================================================================
echo [STEP 2] Committing changes to git...
echo ================================================================
echo.

git add .
git commit -m "Rebranded to PRISM TRADE + rebuilt frontend"

echo.
echo ================================================================
echo [STEP 3] Pushing to GitHub (Railway will auto-deploy)...
echo ================================================================
echo.

git push origin main

if errorlevel 1 (
    echo.
    echo WARNING: Git push failed. Check your git credentials.
    echo You may need to run: git push origin main manually
    pause
    exit /b 1
)

echo.
echo ================================================================
echo DEPLOYMENT COMPLETE!
echo ================================================================
echo.
echo Your app is being deployed to Railway.
echo Check: https://railway.app/dashboard
echo.
echo URL: https://prismtrade-production.up.railway.app
echo.
echo The deployment takes 2-3 minutes.
echo ================================================================
echo.
pause
