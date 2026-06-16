# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Add import
import_text = 'from exchange_connector import ExchangeConnector\n'
import_pos = app_content.find('from api_key_manager import key_manager')
import_newline = app_content.find('\n', import_pos) + 1
app_content = app_content[:import_newline] + import_text + app_content[import_newline:]

# Trading routes with unique names
trading_routes = """
@app.route('/api/trading/balance', methods=['GET'])
def trading_get_balance():
    try:
        auth_header = request.headers.get('Authorization')
        user = get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        exchange = request.args.get('exchange', 'gemini')
        connector = ExchangeConnector(user.id, exchange)
        balance = connector.get_balance()
        
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
        
        if not symbol or not amount:
            return jsonify({'error': 'Symbol and amount required'}), 400
        
        connector = ExchangeConnector(user.id, exchange)
        order = connector.create_market_buy(symbol, float(amount))
        
        return jsonify({'success': True, 'order': order}), 200
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
        
        if not symbol or not amount:
            return jsonify({'error': 'Symbol and amount required'}), 400
        
        connector = ExchangeConnector(user.id, exchange)
        order = connector.create_market_sell(symbol, float(amount))
        
        return jsonify({'success': True, 'order': order}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""

# Add before health check
health_pos = app_content.find("@app.route('/api/health'")
app_content = app_content[:health_pos] + trading_routes + app_content[health_pos:]

# Write
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

print('Done!')