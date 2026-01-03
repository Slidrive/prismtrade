from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import init_db, DBSession
from models import User, Strategy, Backtest, Trade, StrategyStatus, TradingMode
from auth import hash_password, verify_password, create_access_token, get_user_from_token
from gemini_api import gemini
from datetime import datetime
import os

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

with app.app_context():
    init_db()
    print("Database initialized")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

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
            existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
            if existing:
                return jsonify({'error': 'User already exists'}), 400
            user = User(username=username, email=email, password_hash=hash_password(password))
            db.add(user)
            db.commit()
            db.refresh(user)
            token = create_access_token({"sub": str(user.id)})
            return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role.value}}), 201
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
            user = db.query(User).filter((User.username == username) | (User.email == username)).first()
            if not user or not verify_password(password, user.password_hash):
                return jsonify({'error': 'Invalid credentials'}), 401
            user.last_login = datetime.utcnow()
            db.commit()
            token = create_access_token({"sub": str(user.id)})
            return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role.value, 'paper_balance': user.paper_balance}}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        return jsonify({'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role.value, 'paper_balance': user.paper_balance}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/ticker/<pair>', methods=['GET'])
def get_ticker(pair):
    try:
        ticker = gemini.get_ticker(pair.lower())
        if ticker:
            return jsonify(ticker), 200
        return jsonify({'error': 'Pair not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/candles/<pair>/<timeframe>', methods=['GET'])
def get_candles(pair, timeframe):
    try:
        limit = request.args.get('limit', 100, type=int)
        candles = gemini.get_candles(pair.lower(), timeframe, limit)
        return jsonify({'pair': pair, 'timeframe': timeframe, 'candles': candles}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/execute', methods=['POST'])
def execute_trade():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        data = request.json
        pair = data.get('pair')
        side = data.get('side')
        quantity = float(data.get('quantity'))
        price = float(data.get('price'))
        with DBSession() as db:
            user = db.query(User).filter(User.id == user.id).first()
            if side == 'buy':
                required_balance = quantity * price
                if user.paper_balance < required_balance:
                    return jsonify({'error': 'Insufficient paper balance'}), 400
                user.paper_balance -= required_balance
            else:
                user.paper_balance += quantity * price
            trade = Trade(user_id=user.id, pair=pair, side=side, quantity=quantity, price=price, total=quantity * price, status='FILLED', timestamp=datetime.utcnow())
            db.add(trade)
            db.commit()
            db.refresh(trade)
            return jsonify({'trade_id': trade.id, 'pair': trade.pair, 'side': trade.side, 'quantity': trade.quantity, 'price': trade.price, 'total': trade.total, 'new_balance': user.paper_balance, 'timestamp': trade.timestamp.isoformat()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/history', methods=['GET'])
def get_trade_history():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        with DBSession() as db:
            trades = db.query(Trade).filter(Trade.user_id == user.id).order_by(Trade.timestamp.desc()).limit(50).all()
            return jsonify([{'id': t.id, 'pair': t.pair, 'side': t.side, 'quantity': t.quantity, 'price': t.price, 'total': t.total, 'status': t.status, 'timestamp': t.timestamp.isoformat()} for t in trades]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
