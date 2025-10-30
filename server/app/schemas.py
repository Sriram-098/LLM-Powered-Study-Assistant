from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
import re

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Material Schemas
class MaterialBase(BaseModel):
    title: str
    content: str
    file_type: str
    file_url: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int
    uploaded_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True

class GeneratedDataBase(BaseModel):
    summary: Optional[str] = None
    quiz_questions: Optional[str] = None
    key_concepts: Optional[str] = None

class GeneratedData(GeneratedDataBase):
    id: int
    material_id: int
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Response Schemas
class MaterialWithGenerated(BaseModel):
    material: Material
    generated_data: Optional[GeneratedData] = None