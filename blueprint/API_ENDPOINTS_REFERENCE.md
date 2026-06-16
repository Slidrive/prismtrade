================================================================================
PRISMTRADE - COMPLETE API ENDPOINTS REFERENCE
All HTTP endpoints organized by phase
================================================================================

BASE URL:
Local: http://localhost:5000
Production: https://prismtrade-production.up.railway.app

All endpoints require Authorization header:
Authorization: Bearer <JWT_TOKEN>

================================================================================
AUTHENTICATION ENDPOINTS
================================================================================

POST /api/auth/register
Request: {username, email, password}
Response: {success: true, message: "User registered"}

POST /api/auth/login
Request: {email, password}
Response: {success: true, token: "JWT_TOKEN"}

POST /api/auth/refresh
Request: {}
Response: {success: true, token: "NEW_JWT_TOKEN"}

================================================================================
PHASE 1: SECURE API KEY STORAGE & LIVE TRADING
================================================================================

POST /api/api-keys/store
Request: {exchange: "binance", api_key: "xxx", api_secret: "xxx"}
Response: {success: true, message: "API keys stored"}

GET /api/api-keys/list
Response: {keys: [{id, exchange, is_active, created_at}]}

DELETE /api/api-keys/<id>
Response: {success: true}

POST /api/api-keys/test-connection
Request: {exchange: "binance"}
Response: {success: true, balance: 5000.50}

POST /api/trading/place-order
Request: {exchange, symbol: "BTC/USDT", side: "buy", amount: 0.01, type: "market"}
Response: {success: true, order: {...}}

GET /api/trading/positions?exchange=binance
Response: {positions: {BTC: {...}, ETH: {...}}}

GET /api/trading/history
Response: {trades: [{id, symbol, side, entry_price, exit_price, profit_loss}]}

================================================================================
PHASE 2: COPY TRADING
================================================================================

GET /api/copy-trading/masters?limit=20
Response: {masters: [{user_id, username, monthly_return, followers, success_rate}]}

POST /api/copy-trading/follow
Request: {master_id: 5, copy_percentage: 100.0}
Response: {success: true, follow_id: 123}

POST /api/copy-trading/unfollow
Request: {master_id: 5}
Response: {success: true}

GET /api/copy-trading/following
Response: {following: [{master_username, copy_percentage, total_profit}]}

GET /api/copy-trading/my-followers
Response: {followers: [...], total_followers: 145}

================================================================================
PHASE 3: LEADERBOARD
================================================================================

GET /api/leaderboard/monthly?limit=100
Response: {month: "2025-10", leaderboard: [{rank, username, monthly_pnl, monthly_return_pct, win_rate}]}

GET /api/leaderboard/all-time
Response: {leaderboard: [{rank, username, all_time_pnl, total_trades}]}

GET /api/leaderboard/my-rank
Response: {rank: 25, monthly_pnl: 450.25, monthly_return_pct: 9.5, percentile: 0.75}

GET /api/leaderboard/prizes
Response: {prizes: [{rank: 1, prize: 1000.00}, {rank: 2, prize: 500.00}]}

================================================================================
PHASE 4: PREBUILT BOTS
================================================================================

GET /api/bots/available
Response: {bots: [{id, name, description, type, success_rate, active_users}]}

POST /api/bots/activate
Request: {bot_id: 1, symbol: "BTC/USDT", parameters: {...}}
Response: {success: true, active_bot_id: 456}

GET /api/bots/active
Response: {active_bots: [{bot_id, bot_name, symbol, status, total_pnl}]}

PUT /api/bots/<id>/settings
Request: {parameters: {...}}
Response: {success: true}

================================================================================
PHASE 5: GAMIFICATION
================================================================================

GET /api/achievements
Response: {achievements: [{type, title, description, reward_points, earned_at}]}

GET /api/user/level
Response: {level: 5, total_points: 350, experience: 850, experience_to_next: 1000}

POST /api/referral/generate-code
Response: {referral_code: "PRISM2025ABC", referral_link: "..."}

GET /api/referral/stats
Response: {total_referrals: 12, total_bonus_earned: 500.00}

================================================================================
TESTING WITH CURL
================================================================================

curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d ''{"email":"test@test.com","password":"pass"}''

curl -X GET http://localhost:5000/api/user/profile -H "Authorization: Bearer TOKEN"

curl -X GET http://localhost:5000/api/leaderboard/monthly -H "Authorization: Bearer TOKEN"

================================================================================
