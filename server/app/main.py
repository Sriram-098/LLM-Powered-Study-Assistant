from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import auth, materials, llm
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Study Assistant API",
    description="LLM-Powered Study Assistant Backend",
    version="1.0.0"
)

# Configure CORS - Read allowed origins from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(materials.router)
app.include_router(llm.router)

@app.get("/")
def read_root():
    return {"message": "Study Assistant API is running!"}

@app.get("/health")
def health_check():
    from .services.supabase_storage import supabase_storage
    
    return {
        "status": "healthy",
        "storage": {
            "configured": supabase_storage.is_configured(),
            "service": "supabase"
        }
    }

@app.get("/health/storage")
def storage_health_check():
    """Detailed storage configuration check."""
    from .services.supabase_storage import supabase_storage
    
    return {
        "storage_service": "supabase",
        "configuration": supabase_storage.get_configuration_status()
    }