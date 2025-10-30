import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/llm", tags=["llm"])

# Mock LLM functions - replace with actual LLM integration
def generate_summary_mock(content: str) -> str:
    """Mock function to generate summary. Replace with actual LLM call."""
    return f"Summary of the provided content: {content[:200]}..."

def generate_quiz_mock(content: str) -> list:
    """Mock function to generate quiz questions. Replace with actual LLM call."""
    return [
        {
            "question": "What is the main topic discussed in this material?",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A"
        },
        {
            "question": "Explain the key concept mentioned in the text.",
            "type": "short_answer",
            "sample_answer": "Sample answer based on the content."
        }
    ]

def extract_concepts_mock(content: str) -> list:
    """Mock function to extract key concepts. Replace with actual LLM call."""
    return [
        "Key Concept 1",
        "Key Concept 2", 
        "Key Concept 3"
    ]

@router.post("/generate-summary/{material_id}")
def generate_summary(
    material_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Generate summary for uploaded material."""
    # Get material
    material = db.query(models.Material).filter(
        models.Material.id == material_id,
        models.Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Generate summary using LLM
    summary = generate_summary_mock(material.content)
    
    # Check if generated data already exists
    generated_data = db.query(models.GeneratedData).filter(
        models.GeneratedData.material_id == material_id
    ).first()
    
    if generated_data:
        generated_data.summary = summary
    else:
        generated_data = models.GeneratedData(
            material_id=material_id,
            summary=summary
        )
        db.add(generated_data)
    
    db.commit()
    db.refresh(generated_data)
    
    return {"summary": summary}

@router.post("/generate-quiz/{material_id}")
def generate_quiz(
    material_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Generate quiz questions for uploaded material."""
    # Get material
    material = db.query(models.Material).filter(
        models.Material.id == material_id,
        models.Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Generate quiz using LLM
    quiz_questions = generate_quiz_mock(material.content)
    quiz_json = json.dumps(quiz_questions)
    
    # Check if generated data already exists
    generated_data = db.query(models.GeneratedData).filter(
        models.GeneratedData.material_id == material_id
    ).first()
    
    if generated_data:
        generated_data.quiz_questions = quiz_json
    else:
        generated_data = models.GeneratedData(
            material_id=material_id,
            quiz_questions=quiz_json
        )
        db.add(generated_data)
    
    db.commit()
    db.refresh(generated_data)
    
    return {"quiz_questions": quiz_questions}

@router.post("/extract-concepts/{material_id}")
def extract_concepts(
    material_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Extract key concepts from uploaded material."""
    # Get material
    material = db.query(models.Material).filter(
        models.Material.id == material_id,
        models.Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Extract concepts using LLM
    key_concepts = extract_concepts_mock(material.content)
    concepts_json = json.dumps(key_concepts)
    
    # Check if generated data already exists
    generated_data = db.query(models.GeneratedData).filter(
        models.GeneratedData.material_id == material_id
    ).first()
    
    if generated_data:
        generated_data.key_concepts = concepts_json
    else:
        generated_data = models.GeneratedData(
            material_id=material_id,
            key_concepts=concepts_json
        )
        db.add(generated_data)
    
    db.commit()
    db.refresh(generated_data)
    
    return {"key_concepts": key_concepts}