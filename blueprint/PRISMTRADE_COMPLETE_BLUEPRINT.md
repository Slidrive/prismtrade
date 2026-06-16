================================================================================
PRISMTRADE - COMPLETE BLUEPRINT & IMPLEMENTATION GUIDE
================================================================================

PROJECT: AI-Powered Cryptocurrency Trading Platform
STATUS: Phase 1 (70% complete), Phases 2-5 Ready for Implementation
DEPLOYMENT: Railway (prismtrade-production.up.railway.app)

TECH STACK:
- Backend: Python Flask + SQLAlchemy
- Frontend: React 18 + TradingView Charts
- Trading Engine: Freqtrade
- Market Data: Gemini API
- Authentication: JWT tokens
- Deployment: Railway.app

DATABASE SCHEMA:

users table:
├─ id (primary key)
├─ username
├─ email
├─ password_hash
├─ balance (paper trading)
└─ created_at

strategies table:
├─ id
├─ user_id
├─ name
├─ description
├─ type (custom/prebuilt)
└─ parameters

backtests table:
├─ id
├─ strategy_id
├─ start_date
├─ end_date
├─ results (JSON)
└─ status

trades table:
├─ id
├─ user_id
├─ symbol
├─ entry_price
├─ exit_price
├─ quantity
└─ profit_loss

api_keys table (PHASE 1):
├─ id
├─ user_id
├─ exchange
├─ encrypted_key
├─ encrypted_secret
└─ is_active

copy_trading table (PHASE 2):
├─ id
├─ follower_id
├─ master_trader_id
├─ copy_percentage
└─ status

leaderboard table (PHASE 3):
├─ id
├─ user_id
├─ rank
├─ monthly_pnl
└─ month

prebuilt_bots table (PHASE 4):
├─ id
├─ name
├─ type
├─ default_params
└─ active_users

achievements table (PHASE 5):
├─ id
├─ user_id
├─ achievement_type
├─ earned_at
└─ reward_points

================================================================================
PHASE 1 IMPLEMENTATION: SECURE API KEY STORAGE & LIVE TRADING
================================================================================

Key Files:
1. api_key_manager.py - Encryption/decryption
2. live_trading.py - Exchange integration
3. models.py - Database tables
4. app.py - API endpoints

Models to add to models.py:

class APIKey(db.Model):
    __tablename__ = ''api_keys''
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(''user.id''))
    exchange = db.Column(db.String(50))
    encrypted_key = db.Column(db.Text)
    encrypted_secret = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship(''User'', backref=''api_keys'')

class Trade(db.Model):
    __tablename__ = ''trade''
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(''user.id''))
    symbol = db.Column(db.String(20))
    side = db.Column(db.String(10))
    quantity = db.Column(db.Float)
    entry_price = db.Column(db.Float)
    exit_price = db.Column(db.Float)
    profit_loss = db.Column(db.Float)
    trade_type = db.Column(db.String(20), default=''PAPER'')
    status = db.Column(db.String(20), default=''OPEN'')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship(''User'', backref=''trades'')

API Endpoints (app.py):

POST /api/api-keys/store
Purpose: Store encrypted API keys
Request: {exchange, api_key, api_secret}
Response: {success: true}

GET /api/api-keys/list
Purpose: List stored keys (no secrets)
Response: {keys: [{id, exchange, is_active, created_at}]}

DELETE /api/api-keys/<id>
Purpose: Delete an API key
Response: {success: true}

POST /api/api-keys/test-connection
Purpose: Test if API keys work
Response: {success: true, balance: 5000}

POST /api/trading/place-order
Purpose: Execute real trade
Request: {exchange, symbol, side, amount, type, price}
Response: {success: true, order: {...}}

GET /api/trading/positions
Purpose: Get open positions
Response: {positions: {...}}

GET /api/trading/history
Purpose: Get trade history
Response: {trades: [...]}

================================================================================
PHASES 2-5: CODE READY FOR IMPLEMENTATION
================================================================================

PHASE 2: COPY TRADING
- Master trader profiles
- Follower mechanism
- Profit sharing (20% default fee)
- Copy execution engine

PHASE 3: LEADERBOARD
- Monthly rankings
- Prize pool distribution ($1000+/month)
- User tier system
- Leaderboard UI display

PHASE 4: PREBUILT BOTS
- DCA Bot (Dollar Cost Averaging)
- Grid Trading Bot
- RSI Scalping Bot
- Bot activation & monitoring

PHASE 5: GAMIFICATION
- Achievement system
- Level progression
- Referral rewards
- Experience points

================================================================================
DEPLOYMENT CHECKLIST
================================================================================

Before deploying to Railway:

✅ Test locally with 3 terminals
✅ Verify all imports work
✅ Test API endpoints with curl
✅ Check database migrations
✅ Review git status
✅ Make small commits
✅ Push to GitHub
✅ Wait for Railway auto-deploy
✅ Add secrets to Railway (MASTER_KEY)
✅ Verify production URL works

================================================================================
