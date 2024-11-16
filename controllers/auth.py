# controllers/auth.py

from models.models import User
from models.database import session_scope
#from sqlalchemy.orm import Session
import hashlib
import os

# Hash the password using SHA-256
def hash_password(password: str) -> str:
    salt = os.urandom(16) 
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return salt.hex() + ":" + hashed

# Verify hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt, stored_hash = hashed_password.split(":")
    hashed = hashlib.sha256(bytes.fromhex(salt) + plain_password.encode()).hexdigest()
    return hashed == stored_hash

# Create User
def create_user(username: str, password: str):
    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password)
    with session_scope() as db:
        db.add(user)
        db.commit() # commit is done in session_scope
        db.refresh(user)
    return user

# Authenticate User
def authenticate_user(username: str, password: str):
    with session_scope() as db:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password):
            return user
    return None