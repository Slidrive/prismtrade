# Read the trading routes
with open('trading_endpoints.txt', 'r', encoding='utf-8') as f:
    routes_content = f.read()

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Extract imports
import_text = 'from exchange_connector import ExchangeConnector\n'

# Add import after api_key_manager import
import_pos = app_content.find('from api_key_manager import key_manager')
import_newline = app_content.find('\n', import_pos) + 1
app_content = app_content[:import_newline] + import_text + app_content[import_newline:]

# Extract routes (everything after first @app.route)
route_start = routes_content.find('@app.route')
routes = routes_content[route_start:].strip()

# Add routes before health check
health_pos = app_content.find("@app.route('/api/health'")
app_content = app_content[:health_pos] + '\n' + routes + '\n\n' + app_content[health_pos:]

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

print('Trading routes added!')