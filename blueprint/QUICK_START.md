================================================================================
PRISMTRADE - QUICK START GUIDE (START HERE!)
Copy-paste these commands to get Phase 1 working
================================================================================

Time: 45 minutes

STEP 1: Verify environment (5 minutes)
python --version (should be 3.11+)
node --version (should be 18+)
npm --version (should be 9+)
git status (should show clean)

STEP 2: Create Phase 1 files (15 minutes)

In C:\Users\skidr\trading_platform run:

@''
from cryptography.fernet import Fernet
import os

class APIKeyManager:
    def __init__(self, master_key=None):
        if master_key is None:
            master_key = os.getenv("MASTER_KEY")
        self.cipher_suite = Fernet(master_key)
    
    @staticmethod
    def generate_master_key():
        return Fernet.generate_key().decode()
    
    def encrypt_key(self, api_key):
        return self.cipher_suite.encrypt(api_key.encode()).decode()
    
    def decrypt_key(self, encrypted_key):
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
''@ | Out-File api_key_manager.py -Encoding utf8

STEP 3: Generate MASTER_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
SAVE THIS KEY!

STEP 4: Create .env file
@''
MASTER_KEY=paste_your_key_here
FLASK_ENV=development
''@ | Out-File .env -Encoding utf8

STEP 5: Install dependencies
pip install cryptography==41.0.0 ccxt==4.0.0

STEP 6: Test locally (20 minutes)
Terminal 1: python app.py
Terminal 2: cd frontend && npm start
Terminal 3: curl http://localhost:5000/api/health

STEP 7: Deploy to Railway (5 minutes)
git add .
git commit -m "Phase 1: Add secure API key storage"
git push origin main

Go to https://dashboard.railway.app
Wait for green checkmark
Add MASTER_KEY to Variables

DONE! Phase 1 is deployed! 🎉

Next: Read POWERSHELL_COMMANDS.md for Phases 2-5

================================================================================
