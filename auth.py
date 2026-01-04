from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "test-secret-key")

def hash_password(password):
    return generate_password_hash(password)

def verify_password(plain, hashed):
    return check_password_hash(hashed, plain)

def create_access_token(data):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(hours=24)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_user_from_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"user_id": int(payload.get("sub"))}
    except:
        return None