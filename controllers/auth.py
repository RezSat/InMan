# controllers/auth.py

from models.models import User
from sqlalchemy.orm import Session
import hashlib
import os

# Hash the password using SHA-256
def hash_password(password: str) -> str:
    # Generate a random salt
    salt = os.urandom(16)  # 16 bytes of random salt
    # Hash the password with the salt
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    # Store the salt and the hashed password together
    return salt.hex() + ":" + hashed

# Verify hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Split the stored hashed password to get the salt and the hash
    salt, stored_hash = hashed_password.split(":")
    # Recreate the hash using the provided password and the stored salt
    hashed = hashlib.sha256(bytes.fromhex(salt) + plain_password.encode()).hexdigest()
    return hashed == stored_hash

# Create User
def create_user(db: Session, username: str, password: str):
    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Authenticate User
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        return user
    return None