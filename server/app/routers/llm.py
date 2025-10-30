import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from ..services.gemini_service import gemini_service

router = APIRouter(prefix="/llm", tags=["llm"])

@router.post("/generate-summary/{material_id}")
def generate_summary(
    material_id: int,
    max_length: Optional[int] = Query(300, description="Maximum length of summary in words"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Generate summary for uploaded material using Gemini AI."""
    # Get material
    material = db.query(models.Material).filter(
        models.Material.id == material_id,
        models.Material.user_id == current_user.id
    ).first()

    print(material)
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    if not material.content or len(material.content.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material content is too short to generate a meaningful summary"
        )
    
    # Generate summary using Gemini AI
    try:
        summary = gemini_service.generate_summary(material.content, max_length)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )
    
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
    
    return {
        "summary": summary,
        "material_id": material_id,
        "material_title": material.title,
        "word_count": len(summary.split())
    }

@router.post("/generate-quiz/{material_id}")
def generate_quiz(
    material_id: int,
    num_mcq: Optional[int] = Query(10, description="Number of multiple choice questions to generate"),
    num_short: Optional[int] = Query(5, description="Number of short answer questions to generate"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Generate quiz questions for uploaded material using Gemini AI."""
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
    
    if not material.content or len(material.content.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material content is too short to generate meaningful quiz questions"
        )
    
    # Validate number of questions
    if num_mcq < 1 or num_mcq > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of MCQ questions must be between 1 and 50"
        )
    
    if num_short < 1 or num_short > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of short answer questions must be between 1 and 20"
        )
    
    # Generate quiz using Gemini AI
    try:
        quiz_questions = gemini_service.generate_quiz(material.content, num_mcq, num_short)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )
    
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
    
    return {
        "quiz_questions": quiz_questions,
        "material_id": material_id,
        "material_title": material.title,
        "total_questions": len(quiz_questions),
        "question_types": list(set(q.get("type", "unknown") for q in quiz_questions))
    }

@router.post("/extract-concepts/{material_id}")
def extract_concepts(
    material_id: int,
    max_concepts: Optional[int] = Query(10, description="Maximum number of concepts to extract"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Extract key concepts from uploaded material using Gemini AI."""
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
    
    if not material.content or len(material.content.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material content is too short to extract meaningful concepts"
        )
    
    # Validate max concepts
    if max_concepts < 1 or max_concepts > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum concepts must be between 1 and 50"
        )
    
    try:
        key_concepts = gemini_service.extract_concepts(material.content, max_concepts)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract concepts: {str(e)}"
        )
    
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
    
    return {
        "key_concepts": key_concepts,
        "material_id": material_id,
        "material_title": material.title,
        "total_concepts": len(key_concepts)
    }

@router.post("/analyze-material/{material_id}")
def analyze_material(
    material_id: int,
    max_summary_length: Optional[int] = Query(300, description="Maximum length of summary in words"),
    num_mcq: Optional[int] = Query(10, description="Number of multiple choice questions to generate"),
    num_short: Optional[int] = Query(5, description="Number of short answer questions to generate"),
    max_concepts: Optional[int] = Query(10, description="Maximum number of concepts to extract"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Comprehensive analysis: generate summary, quiz, and extract concepts in one call."""
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
    
    if not material.content or len(material.content.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material content is too short for comprehensive analysis"
        )
    
    results = {}
    errors = {}
    
    # Generate summary
    try:
        summary = gemini_service.generate_summary(material.content, max_summary_length)
        results["summary"] = summary
    except Exception as e:
        errors["summary"] = str(e)
        results["summary"] = None
    
    # Generate quiz
    try:
        quiz_questions = gemini_service.generate_quiz(material.content, num_mcq, num_short)
        results["quiz_questions"] = quiz_questions
    except Exception as e:
        errors["quiz"] = str(e)
        results["quiz_questions"] = []
    
    # Extract concepts
    try:
        key_concepts = gemini_service.extract_concepts(material.content, max_concepts)
        results["key_concepts"] = key_concepts
    except Exception as e:
        errors["concepts"] = str(e)
        results["key_concepts"] = []
    
    # Save to database if at least one operation succeeded
    if any(results.values()):
        generated_data = db.query(models.GeneratedData).filter(
            models.GeneratedData.material_id == material_id
        ).first()
        
        if generated_data:
            if results["summary"]:
                generated_data.summary = results["summary"]
            if results["quiz_questions"]:
                generated_data.quiz_questions = json.dumps(results["quiz_questions"])
            if results["key_concepts"]:
                generated_data.key_concepts = json.dumps(results["key_concepts"])
        else:
            generated_data = models.GeneratedData(
                material_id=material_id,
                summary=results["summary"],
                quiz_questions=json.dumps(results["quiz_questions"]) if results["quiz_questions"] else None,
                key_concepts=json.dumps(results["key_concepts"]) if results["key_concepts"] else None
            )
            db.add(generated_data)
        
        db.commit()
        db.refresh(generated_data)
    
    response = {
        "material_id": material_id,
        "material_title": material.title,
        "analysis_results": results,
        "success_count": sum(1 for v in results.values() if v),
        "total_operations": 3
    }
    
    if errors:
        response["errors"] = errors
    
    return response

@router.get("/status")
def get_llm_status():
    """Get the status of the LLM service."""
    return {
        "service": "Google Gemini AI",
        "model": "gemini-pro",
        "configured": gemini_service.is_configured(),
        "features": {
            "summarization": gemini_service.is_configured(),
            "quiz_generation": gemini_service.is_configured(),
            "concept_extraction": gemini_service.is_configured()
        }
    }