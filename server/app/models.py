from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    materials = relationship("Material", back_populates="owner")

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    file_type = Column(String, nullable=False)  # 'pdf' or 'text'
    file_url = Column(String, nullable=True)  # S3 URL for PDF files
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="materials")
    generated_data = relationship("GeneratedData", back_populates="material")

class GeneratedData(Base):
    __tablename__ = "generated_data"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    summary = Column(Text)
    quiz_questions = Column(Text)  # JSON string of questions
    key_concepts = Column(Text)    # JSON string of concepts
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    material = relationship("Material", back_populates="generated_data")