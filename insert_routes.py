# Read the routes we want to add
with open('api_key_routes_complete.txt', 'r', encoding='utf-8') as f:
    routes_content = f.read()

# Read current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Extract imports and routes
import_start = routes_content.find('from api_key_manager')
import_end = routes_content.find('\n', routes_content.find('from models import APIKey')) + 1
imports = routes_content[import_start:import_end].strip()

routes_start = routes_content.find('@app.route')
routes = routes_content[routes_start:].strip()

# Add imports after 'from datetime import datetime'
import_pos = app_content.find('from datetime import datetime')
import_newline = app_content.find('\n', import_pos) + 1
app_content = app_content[:import_newline] + imports + '\n' + app_content[import_newline:]

# Add routes before health check
health_pos = app_content.find("@app.route('/api/health'")
app_content = app_content[:health_pos] + '\n' + routes + '\n\n' + app_content[health_pos:]

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

print('✅ API key routes added successfully!')
