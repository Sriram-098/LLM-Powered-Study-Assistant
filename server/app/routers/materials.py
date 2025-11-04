from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from ..services.supabase_storage import supabase_storage
from ..services.gemini_service import gemini_service
import PyPDF2
import io
import json
from pydantic import BaseModel

router = APIRouter(prefix="/materials", tags=["materials"])

# Pydantic model for text upload
class TextUpload(BaseModel):
    title: str
    content: str

def auto_process_with_llm_background(material_id: int, content: str, db_session):
    """
    Background task to process uploaded material with LLM.
    Runs asynchronously without blocking the upload response.
    """
    from ..database import SessionLocal
    
    # Create new database session for background task
    db = SessionLocal()
    
    try:
        if not content or len(content.strip()) < 50:
            print(f"⚠ Content too short for LLM processing: {len(content.strip())} characters")
            return
        
        if not gemini_service.is_configured():
            print("⚠ LLM service not configured - skipping automatic processing")
            return
        
        print(f"🤖 Starting background LLM processing for material ID: {material_id}")
        
        # Initialize results
        summary = None
        quiz_questions = None
        key_concepts = None
        
        # Optimize content size for faster processing
        content_to_process = content[:8000] if len(content) > 8000 else content
        
        # 1. Generate summary (fastest)
        try:
            print("📝 Generating summary...")
            summary = gemini_service.generate_summary(content_to_process, max_length=300)
            print(f"✅ Summary generated")
        except Exception as e:
            print(f"❌ Failed to generate summary: {e}")
        
        # 2. Extract key concepts (fast)
        try:
            print("🔍 Extracting key concepts...")
            key_concepts = gemini_service.extract_concepts(content_to_process, max_concepts=10)
            print(f"✅ Key concepts extracted")
        except Exception as e:
            print(f"❌ Failed to extract key concepts: {e}")
        
        # 3. Create quiz questions (slower)
        try:
            print("❓ Creating quiz questions...")
            quiz_questions = gemini_service.generate_quiz(content_to_process, num_mcq=6, num_short=3)
            print(f"✅ Quiz questions created")
        except Exception as e:
            print(f"❌ Failed to create quiz questions: {e}")
        
        # Save all generated data to database
        if summary or quiz_questions or key_concepts:
            generated_data = models.GeneratedData(
                material_id=material_id,
                summary=summary,
                quiz_questions=json.dumps(quiz_questions) if quiz_questions else None,
                key_concepts=json.dumps(key_concepts) if key_concepts else None
            )
            db.add(generated_data)
            db.commit()
            print(f"💾 LLM data saved for material ID: {material_id}")
        else:
            print("⚠ No LLM data was generated")
            
    except Exception as e:
        print(f"❌ Error in background LLM processing: {e}")
        db.rollback()
    finally:
        db.close()

async def auto_process_with_llm(material: models.Material, db: Session):
    """
    Legacy function - kept for compatibility.
    Now just calls the background version.
    """
    print(f"🤖 Starting automatic LLM processing for material: {material.title}")
    
    try:
        # Initialize results
        summary = None
        quiz_questions = None
        key_concepts = None
        
        # Optimize content size for faster processing (use first 5000 chars for large files)
        content_to_process = material.content[:5000] if len(material.content) > 5000 else material.content
        
        # 1. Generate concise summary (fastest)
        try:
            print("📝 Generating concise summary...")
            summary = gemini_service.generate_summary(content_to_process)
            print(f"✅ Summary generated successfully ({len(summary)} characters)")
        except Exception as e:
            print(f"❌ Failed to generate summary: {e}")
        
        # 2. Extract key concepts (fast)
        try:
            print("🔍 Extracting key concepts and terms...")
            key_concepts = gemini_service.extract_concepts(content_to_process, max_concepts=10)
            print(f"✅ Key concepts extracted successfully ({len(key_concepts)} concepts)")
        except Exception as e:
            print(f"❌ Failed to extract key concepts: {e}")
        
        # 3. Create quiz questions (slower - reduced count for speed)
        try:
            print("❓ Creating quiz questions for revision...")
            quiz_questions = gemini_service.generate_quiz(content_to_process, num_mcq=6, num_short=3)
            print(f"✅ Quiz questions created successfully ({len(quiz_questions)} questions)")
        except Exception as e:
            print(f"❌ Failed to create quiz questions: {e}")
        
        # Save all generated data to database
        if summary or quiz_questions or key_concepts:
            generated_data = models.GeneratedData(
                material_id=material.id,
                summary=summary,
                quiz_questions=json.dumps(quiz_questions) if quiz_questions else None,
                key_concepts=json.dumps(key_concepts) if key_concepts else None
            )
            db.add(generated_data)
            db.commit()
            db.refresh(generated_data)
            
            print(f"💾 All LLM-generated data saved to database for material: {material.title}")
            return generated_data
        else:
            print("⚠ No LLM data was generated successfully")
            return None
            
    except Exception as e:
        print(f"❌ Error in automatic LLM processing: {e}")
        return None

@router.post("/upload-material", response_model=schemas.Material)
async def upload_material(
    background_tasks: BackgroundTasks,
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Upload study material (PDF or text file). AI processing happens in background for instant response."""
    content = ""
    file_type = ""
    file_url = None
    
    # Read file content
    file_content = await file.read()
    
    # Process file based on type
    if file.content_type == "application/pdf":
        file_type = "pdf"
        
        # Extract text content from PDF with better formatting preservation
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text.strip():  # Only add non-empty pages
                content += page_text
                # Add page separator for multi-page PDFs
                if page_num < len(pdf_reader.pages) - 1:
                    content += "\n\n--- Page {} ---\n\n".format(page_num + 2)
        
        # Upload PDF to Supabase Storage
        if not supabase_storage.supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage service is not configured. Please check Supabase settings."
            )
        
        try:
            file_url = supabase_storage.upload_file(
                file_content=file_content,
                file_name=file.filename or f"{title}.pdf",
                content_type=file.content_type,
                user_id=current_user.id
            )
            print(f"PDF uploaded successfully: {file_url}")
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            print(f"File upload error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload PDF file: {str(e)}"
            )
            
    elif file.content_type == "text/plain":
        file_type = "text"
        # Try different encodings to preserve original formatting
        try:
            content = file_content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = file_content.decode("utf-8-sig")  # UTF-8 with BOM
            except UnicodeDecodeError:
                try:
                    content = file_content.decode("latin-1")
                except UnicodeDecodeError:
                    content = file_content.decode("utf-8", errors="replace")
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload PDF or text files only."
        )
    
    db_material = models.Material(
        title=title,
        content=content,
        file_type=file_type,
        file_url=file_url,
        user_id=current_user.id
    )
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    # Process with LLM in background for instant response
    background_tasks.add_task(
        auto_process_with_llm_background,
        material_id=db_material.id,
        content=content,
        db_session=db
    )
    
    print(f"✅ Material uploaded instantly. AI processing queued in background.")
    
    return db_material

@router.post("/upload-text", response_model=schemas.Material)
async def upload_text(
    background_tasks: BackgroundTasks,
    text_data: TextUpload,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Upload text content directly."""
    
    # Validate input
    if not text_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )
    
    if not text_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    if len(text_data.content.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content must be at least 50 characters long"
        )
    
    # Create material record
    db_material = models.Material(
        title=text_data.title.strip(),
        content=text_data.content,  # Don't strip content to preserve formatting
        file_type="text",
        file_url=None,  # No file URL for direct text input
        user_id=current_user.id
    )
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    # Process with LLM in background for instant response
    background_tasks.add_task(
        auto_process_with_llm_background,
        material_id=db_material.id,
        content=text_data.content,
        db_session=db
    )
    
    print(f"✅ Text uploaded instantly. AI processing queued in background.")
    
    return db_material

@router.get("/get-history", response_model=List[schemas.MaterialWithGenerated])
def get_user_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's material upload history."""
    materials = db.query(models.Material).filter(
        models.Material.user_id == current_user.id
    ).order_by(models.Material.uploaded_at.desc()).all()
    
    result = []
    for material in materials:
        generated_data = db.query(models.GeneratedData).filter(
            models.GeneratedData.material_id == material.id
        ).first()
        
        result.append({
            "material": material,
            "generated_data": generated_data
        })
    
    return result

@router.get("/{material_id}", response_model=schemas.MaterialWithGenerated)
def get_material(
    material_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific material by ID."""
    material = db.query(models.Material).filter(
        models.Material.id == material_id,
        models.Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    generated_data = db.query(models.GeneratedData).filter(
        models.GeneratedData.material_id == material.id
    ).first()
    
    return {
        "material": material,
        "generated_data": generated_data
    }

@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a material and its associated file."""
    material = db.query(models.Material).filter(
        models.Material.id == material_id,
        models.Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Delete file from Supabase Storage if it exists
    if material.file_url and supabase_storage.supabase:
        try:
            success = supabase_storage.delete_file(material.file_url)
            if success:
                print(f"File deleted successfully: {material.file_url}")
            else:
                print(f"Failed to delete file: {material.file_url}")
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    db.query(models.GeneratedData).filter(
        models.GeneratedData.material_id == material_id
    ).delete()
    
    # Delete material
    db.delete(material)
    db.commit()
    
    return {"message": "Material deleted successfully"}

@router.get("/download/{material_id}")
def get_download_url(
    material_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get download URL for a material file."""
    material = db.query(models.Material).filter(
        models.Material.id == material_id,
        models.Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    if not material.file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file associated with this material"
        )
    
    if not supabase_storage.supabase:
        return {"download_url": material.file_url}
    
    try:
        download_url = supabase_storage.generate_presigned_url(material.file_url)
        return {"download_url": download_url}
    except Exception as e:
        print(f"Error generating download URL: {e}")
        # Fallback to direct URL
        return {"download_url": material.file_url}