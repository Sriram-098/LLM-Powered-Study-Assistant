from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from ..services.supabase_storage import supabase_storage
import PyPDF2
import io

router = APIRouter(prefix="/materials", tags=["materials"])

@router.post("/upload-material", response_model=schemas.Material)
async def upload_material(
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Upload study material (PDF or text file)."""
    content = ""
    file_type = ""
    file_url = None
    
    # Read file content
    file_content = await file.read()
    
    # Process file based on type
    if file.content_type == "application/pdf":
        file_type = "pdf"
        
        # Extract text content from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
        
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
        content = file_content.decode("utf-8")
        
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