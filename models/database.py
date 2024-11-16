# models/database.py

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager 
import logging

logging.basicConfig(level=logging.INFO)

# Database Configuration
DATABASE_URL = "sqlite:///inventory.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_database_initialized():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return len(tables) > 0
        
def initialize_database():
    if is_database_initialized():
        print("Database already initialized.")
        return None
    else:
        Base.metadata.create_all(bind=engine)
        print("Database initialized with SQLAlchemy.")
        return None

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        
        yield session # yield the sessio to the caller
        session.commit()
    except Exception:
        session.rollback() # rollback in case of error
        raise
    finally:
        session.close()