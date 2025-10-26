from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import init_db, DBSession
from models import User, Strategy, Backtest, Trade, StrategyStatus, TradingMode
from auth import hash_password, verify_password, create_access_token, get_user_from_token
from datetime import datetime
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

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)