# Read current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports at the top
new_imports = '''from api_key_manager import key_manager
from models import APIKey
'''

import_location = content.rfind('from datetime import')
import_end = content.find('\n', import_location) + 1
content = content[:import_end] + new_imports + content[import_end:]

# API routes - simplified for now
api_routes = '''
@app.route('/api/api-keys/test', methods=['GET'])
def test_api_keys():
    return jsonify({'message': 'API key endpoints ready'}), 200

'''

health_check_pos = content.find("@app.route('/api/health'")
content = content[:health_check_pos] + api_routes + content[health_check_pos:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')