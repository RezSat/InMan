# main.py
from models.database import engine
from models.models import Base

# Initialize database
def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized with SQLAlchemy.")

if __name__ == "__main__":
    initialize_database()
