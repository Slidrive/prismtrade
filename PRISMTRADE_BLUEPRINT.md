# PRISMTRADE PROJECT BLUEPRINT
**Last Updated:** Oct 26, 2025  
**Status:** Frontend built, backend running on Railway, needs frontend integration

## 🎯 PROJECT OVERVIEW
Prismtrade is a multi-user cryptocurrency trading platform with strategy backtesting, paper trading, and live trading capabilities.

## 🛠 TECH STACK
**Backend:** Python 3.13, Flask, SQLAlchemy, Freqtrade, JWT auth
**Frontend:** React with cyberpunk UI (green #00FF00, cyan accents)
**Database:** SQLite
**Deployment:** Railway, GitHub

## 📊 CURRENT STATUS
✅ Backend running on Railway (prismtrade-production.up.railway.app)
✅ React frontend built with cyberpunk styling
🔄 Needs: Frontend serving from Flask
❌ TODO: Live charts, market data, advanced strategy builder, AI assistant

## 🔗 GitHub
https://github.com/Slidrive/prismtrade.git

## 📁 Key Files
- app.py (main Flask app)
- frontend/build/ (React production build)
- requirements.txt (Python dependencies from venv)
- Procfile (Railway config: web: python app.py)
- trading.db (SQLite database)

## 🚀 NEXT STEP
Add static file serving to app.py to serve React frontend from Flask
