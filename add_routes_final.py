# Read files
with open('api_key_routes_complete.txt', 'r', encoding='utf-8') as f:
    routes = f.read()
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Extract imports
imports = 'from api_key_manager import key_manager\nfrom models import APIKey\n'

# Extract routes
route_start = routes.find('@app.route')
clean_routes = routes[route_start:].strip()

# Add imports
datetime_import = 'from datetime import datetime'
app = app.replace(datetime_import, datetime_import + '\n' + imports)

# Add routes before health check
health = "@app.route('/api/health'"
app = app.replace(health, clean_routes + '\n\n' + health)

# Save
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)
print('Routes added!')