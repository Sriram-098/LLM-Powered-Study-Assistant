from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling and better configuration
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,         # Reduced for Supabase
        max_overflow=10,     # Reduced for Supabase
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=1800,   # Recycle connections every 30 minutes (Supabase timeout)
        echo=False,          # Set to True for SQL debugging
        connect_args={
            "sslmode": "disable" if "localhost" in DATABASE_URL or "@db:" in DATABASE_URL else "require",
            "connect_timeout": 10,
            "application_name": "study_assistant"
        }
    )
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Failed to create database engine: {e}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    """Test database connection with detailed error reporting."""
    if not engine:
        return {"status": "error", "error": "Database engine not initialized"}
    
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            # Get database info
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
            return {
                "status": "connected", 
                "test_result": test_value,
                "database_version": version.split()[0:2],  # PostgreSQL version
                "connection_info": {
                    "pool_size": engine.pool.size(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow(),
                }
            }
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        
        # Provide helpful error suggestions
        suggestions = []
        if "authentication failed" in error_msg.lower():
            suggestions.append("Check username and password in DATABASE_URL")
        elif "could not connect" in error_msg.lower():
            suggestions.append("Check if database server is running and accessible")
        elif "ssl" in error_msg.lower():
            suggestions.append("Check SSL configuration - Supabase requires SSL")
        elif "timeout" in error_msg.lower():
            suggestions.append("Database connection timeout - check network connectivity")
        
        return {
            "status": "error", 
            "error": error_msg,
            "error_type": error_type,
            "suggestions": suggestions
        }