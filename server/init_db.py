from app.database import engine
from app import models

def init_database():
    """Initialize database tables."""
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")

if __name__ == "__main__":
    init_database()