from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import init_db, DBSession
from models import User, Trade
from auth import hash_password, verify_password, create_access_token, get_user_from_token
from gemini_api import gemini
from datetime import datetime
import os

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

with app.app_context():
    init_db()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    return send_from_directory('frontend/build', 'index.html')

def get_current_user(token):
    if not token or not token.startswith('Bearer '):
        return None
    token = token.replace('Bearer ', '')
    user_data = get_user_from_token(token)
    if not user_data:
        return None
    with DBSession() as db:
        return db.query(User).filter(User.id == user_data['user_id']).first()

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        with DBSession() as db:
            user = User(username=data['username'], email=data['email'], password_hash=hash_password(data['password']))
            db.add(user)
            db.commit()
            db.refresh(user)
            token = create_access_token({"sub": str(user.id)})
            return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username}}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        with DBSession() as db:
            user = db.query(User).filter((User.username == data['username']) | (User.email == data['username'])).first()
            if not user or not verify_password(data['password'], user.password_hash):
                return jsonify({'error': 'Invalid credentials'}), 401
            user.last_login = datetime.utcnow()
            db.commit()
            token = create_access_token({"sub": str(user.id)})
            return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'paper_balance': user.paper_balance}}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    user = get_current_user(request.headers.get('Authorization'))
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'id': user.id, 'username': user.username, 'paper_balance': user.paper_balance}), 200

@app.route('/api/market/ticker/<pair>', methods=['GET'])
def get_ticker(pair):
    ticker = gemini.get_ticker(pair.lower())
    if ticker:
        return jsonify(ticker), 200
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/market/candles/<pair>/<timeframe>', methods=['GET'])
def get_candles(pair, timeframe):
    candles = gemini.get_candles(pair.lower(), timeframe, 100)
    return jsonify({'pair': pair, 'timeframe': timeframe, 'candles': candles}), 200

@app.route('/api/trades/execute', methods=['POST'])
def execute_trade():
    user = get_current_user(request.headers.get('Authorization'))
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    with DBSession() as db:
        user = db.query(User).filter(User.id == user.id).first()
        qty, price = float(data['quantity']), float(data['price'])
        if data['side'] == 'buy' and user.paper_balance < qty * price:
            return jsonify({'error': 'Insufficient balance'}), 400
        if data['side'] == 'buy':
            user.paper_balance -= qty * price
        else:
            user.paper_balance += qty * price
        trade = Trade(user_id=user.id, pair=data['pair'], side=data['side'], quantity=qty, price=price, total=qty*price)
        db.add(trade)
        db.commit()
        return jsonify({'trade_id': trade.id, 'new_balance': user.paper_balance}), 201

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)