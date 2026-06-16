@echo off
echo ========================================
echo PrismTrade Railway Deployment
echo ========================================
echo.

cd /d "%~dp0"

echo Checking if build exists...
if not exist "frontend\build\index.html" (
    echo ERROR: Frontend not built yet!
    echo Run build_complete.bat first
    pause
    exit /b 1
)

echo [1/4] Adding all files to git...
git add .

echo [2/4] Committing changes...
git commit -m "Deploy PrismTrade with built frontend"

echo [3/4] Pushing to GitHub...
git push origin main

echo [4/4] DONE!
echo.
echo ========================================
echo Deployment pushed to GitHub
echo Railway will auto-deploy
echo Check: https://railway.app
echo ========================================
echo.
pause
