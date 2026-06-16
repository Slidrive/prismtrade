from cryptography.fernet import Fernet
import os
import base64
from hashlib import sha256

class APIKeyManager:
    def __init__(self):
        # Get encryption key from environment or generate one
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            # Generate a key for development (in production, use a secure key)
            key = base64.urlsafe_b64encode(sha256(b'prismtrade-secret-key').digest())
        else:
            key = key.encode()
        
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        '''Encrypt API key or secret'''
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        '''Decrypt API key or secret'''
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Singleton instance
key_manager = APIKeyManager()
