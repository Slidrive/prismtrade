# PrismTrade Railway Deployment - Fixed Configuration

## 🔧 What Was Fixed

The Railway deployment had THREE configuration files trying to control the build:
1. `railway.toml` - Main Railway config (NOW CORRECT)
2. `nixpacks.toml` - Backup nixpacks config (NOW CORRECT)
3. `Procfile` - Process startup (NOW CORRECT)

**The Problem:** Frontend wasn't being built before the Flask app started.

**The Solution:** Proper build phases that:
1. Install Node.js + Python
2. Install Python deps with pip
3. Install frontend deps with npm
4. Build React app
5. Start gunicorn serving Flask (which serves the built React)

## 🚀 Railway Deployment Steps

### 1. Push to GitHub
```bash
cd C:\Users\skidr\Documents\trading_platform
git add .
git commit -m "Fixed Railway deployment - proper build phases"
git push origin main
```

### 2. Railway Environment Variables
Set these in your Railway project dashboard:
```
PORT=5000
SECRET_KEY=<generate-a-secure-random-key>
```

### 3. Deploy
Railway will auto-deploy from GitHub. It will:
- ✅ Install Python 3.11 + Node.js 18
- ✅ Install Python packages from requirements.txt
- ✅ Install frontend packages (npm ci)
- ✅ Build React production bundle
- ✅ Start gunicorn serving app.py

### 4. Verify
Once deployed, check:
- `https://your-app.railway.app/api/health` → Should return `{"status": "healthy"}`
- `https://your-app.railway.app/` → Should show your React frontend

## 📁 Files Changed

### `railway.toml` (PRIMARY CONFIG)
```toml
[build]
builder = "nixpacks"

[build.nixpacksPlan.phases.setup]
nixPkgs = ["nodejs", "python311"]

[build.nixpacksPlan.phases.install]
cmds = [
  "python -m pip install --upgrade pip",
  "python -m pip install -r requirements.txt",
  "cd frontend && npm install"
]

[build.nixpacksPlan.phases.build]
cmds = [
  "cd frontend && npm run build"
]

[deploy]
startCommand = "gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 4"
```

### `nixpacks.toml` (BACKUP CONFIG)
In case Railway ignores railway.toml, this nixpacks.toml does the same thing.

### `Procfile` (FALLBACK)
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 4
```

### `frontend/.env.production` (NEW)
```
REACT_APP_API_URL=/api
```
This makes React use relative API URLs in production (same domain as Flask).

## 🧪 Local Testing

Test the full build locally before deploying:

```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Start Flask (serves the built React)
python app.py
```

Visit `http://localhost:5000` - should show React frontend making API calls to `/api/*`

## 🔑 Production Secrets

Make sure these are set in Railway:
- `SECRET_KEY` - Used for JWT tokens (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- Database encryption keys are stored in code (api_key_manager.py) - consider moving to env vars for production

## ✅ Deployment Checklist

- [ ] All files committed to git
- [ ] Pushed to GitHub
- [ ] Railway project linked to GitHub repo
- [ ] Environment variables set in Railway dashboard
- [ ] Deployment triggered (automatic or manual)
- [ ] Health endpoint responding at /api/health
- [ ] Frontend loading at root /
- [ ] Can login/register
- [ ] API keys can be stored (encrypted)
- [ ] Trading endpoints functional

## 🐛 If Still Not Working

Check Railway logs for:
1. **Build phase errors** - npm or pip failures
2. **Start phase errors** - gunicorn binding issues
3. **Runtime errors** - database/crypto library issues

Common fixes:
- Add `TA-Lib` system deps if needed: `nixPkgs = ["nodejs", "python311", "ta-lib"]`
- Increase timeout: `--timeout 180`
- Check Python version matches: `python311`

## 📊 What Railway Does

```
SETUP PHASE
├─ Install Node.js 18
└─ Install Python 3.11

INSTALL PHASE  
├─ pip install requirements.txt (backend deps)
└─ npm ci in frontend/ (frontend deps)

BUILD PHASE
└─ npm run build in frontend/ (creates frontend/build/)

START PHASE
└─ gunicorn app:app (serves Flask + React build)
```

Your Flask app.py already has the correct routes:
```python
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Serves frontend/build/
```

## 🎯 Result

After deployment:
- ✅ React frontend at `https://your-app.railway.app/`
- ✅ API at `https://your-app.railway.app/api/*`
- ✅ One deployment, one URL, no CORS issues
- ✅ Flask serves static React build + handles API routes

DONE. No more "frontend not building" bullshit.
