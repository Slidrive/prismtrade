from exchange_connector import ExchangeConnector
from trading_engine import TradingEngine
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import init_db, DBSession
from models import User, Strategy, Backtest, Trade, StrategyStatus, TradingMode, APIKey
from auth import hash_password, verify_password, create_access_token, get_user_from_token
from datetime import datetime
from api_key_manager import key_manager
import os

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# Initialize database on startup
with app.app_context():
    init_db()
    print("✅ Database initialized")

# ==================== SERVE REACT FRONTEND ====================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

# ==================== AUTH MIDDLEWARE ====================

def get_current_user(token):
    if not token or not token.startswith('Bearer '):
        return None
    token = token.replace('Bearer ', '')
    user_data = get_user_from_token(token)
    if not user_data:
        return None
    with DBSession() as db:
        user = db.query(User).filter(User.id == user_data['user_id']).first()
        return user

# ==================== AUTH ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        with DBSession() as db:
            existing = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing:
                return jsonify({'error': 'User already exists'}), 400

            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password)
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            token = create_access_token({"sub": str(user.id)})

            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value
                }
            }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Missing credentials'}), 400

        with DBSession() as db:
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()

            if not user or not verify_password(password, user.password_hash):
                return jsonify({'error': 'Invalid credentials'}), 401

            user.last_login = datetime.utcnow()
            db.commit()

            token = create_access_token({"sub": str(user.id)})

            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value,
                    'paper_balance': user.paper_balance,
                    'live_balance': user.live_balance
                }
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)

        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'paper_balance': user.paper_balance,
            'live_balance': user.live_balance,
            'max_open_trades': user.max_open_trades,
            'risk_per_trade': user.risk_per_trade
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== STRATEGY ENDPOINTS ====================

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)

        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        with DBSession() as db:
            strategies = db.query(Strategy).filter(Strategy.user_id == user.id).all()

            return jsonify([{
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'exchange': s.exchange,
                'trading_pair': s.trading_pair,
                'timeframe': s.timeframe,
                'parameters': s.parameters,
                'status': s.status.value,
                'trading_mode': s.trading_mode.value,
                'total_trades': s.total_trades,
                'winning_trades': s.winning_trades,
                'losing_trades': s.losing_trades,
                'total_profit': s.total_profit,
                'created_at': s.created_at.isoformat() if s.created_at else None
            } for s in strategies]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)

        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        with DBSession() as db:
            strategy = db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.user_id == user.id
            ).first()

            if not strategy:
                return jsonify({'error': 'Strategy not found'}), 404

            return jsonify({
                'id': strategy.id,
                'name': strategy.name,
                'description': strategy.description,
                'exchange': strategy.exchange,
                'trading_pair': strategy.trading_pair,
                'timeframe': strategy.timeframe,
                'parameters': strategy.parameters,
                'entry_conditions': strategy.entry_conditions,
                'exit_conditions': strategy.exit_conditions,
                'stop_loss_pct': strategy.stop_loss_pct,
                'take_profit_pct': strategy.take_profit_pct,
                'status': strategy.status.value,
                'trading_mode': strategy.trading_mode.value
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies', methods=['POST'])
def create_strategy():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)

        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.json

        with DBSession() as db:
            strategy = Strategy(
                user_id=user.id,
                name=data.get('name'),
                description=data.get('description', ''),
                exchange=data.get('exchange'),
                trading_pair=data.get('trading_pair'),
                timeframe=data.get('timeframe'),
                parameters=data.get('parameters', {}),
                stop_loss_pct=data.get('stop_loss_pct'),
                take_profit_pct=data.get('take_profit_pct'),
                status=StrategyStatus.DRAFT,
                trading_mode=TradingMode.PAPER
            )

            db.add(strategy)
            db.commit()
            db.refresh(strategy)

            return jsonify({'id': strategy.id, 'message': 'Strategy created'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies/<int:strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)

        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        with DBSession() as db:
            strategy = db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.user_id == user.id
            ).first()

            if not strategy:
                return jsonify({'error': 'Strategy not found'}), 404

            db.delete(strategy)
            db.commit()

            return jsonify({'message': 'Strategy deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== API KEY MANAGEMENT ====================

@app.route('/api/api-keys/store', methods=['POST'])
def store_api_key():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        exchange = data.get('exchange')
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        
        if not all([exchange, api_key, api_secret]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        encrypted_key = key_manager.encrypt(api_key)
        encrypted_secret = key_manager.encrypt(api_secret)
        
        with DBSession() as db:
            existing = db.query(APIKey).filter(
                APIKey.user_id == user.id,
                APIKey.exchange == exchange
            ).first()
            
            if existing:
                existing.encrypted_key = encrypted_key
                existing.encrypted_secret = encrypted_secret
                existing.is_active = True
            else:
                new_key = APIKey(
                    user_id=user.id,
                    exchange=exchange,
                    encrypted_key=encrypted_key,
                    encrypted_secret=encrypted_secret
                )
                db.add(new_key)
            
            db.commit()
            return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/api-keys/list', methods=['GET'])
def list_api_keys():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        with DBSession() as db:
            keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
            return jsonify({
                'keys': [{
                    'id': k.id,
                    'exchange': k.exchange,
                    'is_active': k.is_active,
                    'created_at': k.created_at.isoformat()
                } for k in keys]
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/api-keys/<int:key_id>', methods=['DELETE'])
def delete_api_key(key_id):
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        with DBSession() as db:
            key = db.query(APIKey).filter(
                APIKey.id == key_id,
                APIKey.user_id == user.id
            ).first()
            
            if not key:
                return jsonify({'error': 'API key not found'}), 404
            
            db.delete(key)
            db.commit()
            return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/api-keys/test-connection', methods=['POST'])
def test_connection():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        exchange = data.get('exchange', 'gemini')
        
        # Try to connect and get balance
        engine = TradingEngine(user.id, exchange)
        balance = engine.get_balance()
        
        return jsonify({
            'success': True,
            'message': 'Connection successful',
            'balance': balance
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ==================== TRADING ENDPOINTS ====================

@app.route('/api/trading/balance', methods=['GET'])
def trading_get_balance():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        exchange = request.args.get('exchange', 'gemini')
        engine = TradingEngine(user.id, exchange)
        balance = engine.get_balance()
        
        return jsonify({'balance': balance}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/ticker/<symbol>', methods=['GET'])
def trading_get_ticker(symbol):
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        exchange = request.args.get('exchange', 'gemini')
        connector = ExchangeConnector(user.id, exchange)
        connector.connect()
        ticker = connector.get_ticker(symbol)
        
        return jsonify({'ticker': ticker}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/buy', methods=['POST'])
def trading_execute_buy():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        exchange = data.get('exchange', 'gemini')
        symbol = data.get('symbol')
        amount = data.get('amount')
        strategy_id = data.get('strategy_id')
        stop_loss_pct = data.get('stop_loss_pct')
        take_profit_pct = data.get('take_profit_pct')
        mode = data.get('mode', 'paper')          # default to paper for safety
        price = data.get('price')                 # live mark from the chart (paper fills)

        if not symbol or not amount:
            return jsonify({'error': 'Symbol and amount required'}), 400

        engine = TradingEngine(user.id, exchange)
        result = engine.execute_buy(
            symbol=symbol,
            amount=float(amount),
            strategy_id=strategy_id,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            mode=mode,
            price=price
        )

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/sell', methods=['POST'])
def trading_execute_sell():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        exchange = data.get('exchange', 'gemini')
        symbol = data.get('symbol')
        amount = data.get('amount')
        trade_id = data.get('trade_id')
        mode = data.get('mode', 'paper')
        price = data.get('price')

        if not symbol or not amount:
            return jsonify({'error': 'Symbol and amount required'}), 400

        engine = TradingEngine(user.id, exchange)
        result = engine.execute_sell(
            symbol=symbol,
            amount=float(amount),
            trade_id=trade_id,
            mode=mode,
            price=price
        )

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/positions', methods=['GET'])
def get_positions():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        exchange = request.args.get('exchange', 'gemini')
        engine = TradingEngine(user.id, exchange)
        positions = engine.get_open_positions()
        
        return jsonify({'positions': positions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/positions/<int:trade_id>/close', methods=['POST'])
def close_position(trade_id):
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        exchange = request.args.get('exchange', 'gemini')
        engine = TradingEngine(user.id, exchange)
        result = engine.close_position(trade_id)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/history', methods=['GET'])
def get_trade_history():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        limit = request.args.get('limit', 50, type=int)
        exchange = request.args.get('exchange', 'gemini')
        
        engine = TradingEngine(user.id, exchange)
        history = engine.get_trade_history(limit=limit)
        
        return jsonify({'trades': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
