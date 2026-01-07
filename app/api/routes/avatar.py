"""API routes for avatar generation."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AvatarGenerateRequest,
    AvatarResponse,
    AvatarFaceMapRequest,
    ErrorResponse
)
from app.services.avatar_generator import avatar_generator
from app.services.face_mapper import face_mapper
import os
from datetime import datetime

router = APIRouter()


@router.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarGenerateRequest):
    """
    Generate a 2D avatar from body measurements.
    
    Args:
        request: Avatar generation request with measurements and preferences
        
    Returns:
        Generated avatar with ID and image data
    """
    try:
        # Generate avatar
        result = avatar_generator.generate_avatar(
            measurements=request.measurements,
            skin_tone=request.skin_tone,
            gender=request.gender
        )
        
        # If face image provided, add it
        if request.face_image:
            try:
                # Extract and validate face
                face_data = face_mapper.extract_face(request.face_image)
                
                if face_data:
                    # Add face to avatar
                    img_with_face = avatar_generator.add_face_overlay(
                        avatar_path=result["file_path"],
                        face_image_base64=request.face_image
                    )
                    result["image_data"] = img_with_face
            except Exception as e:
                # Continue without face if face mapping fails
                print(f"Face mapping failed: {e}")
        
        return AvatarResponse(
            success=True,
            avatar_id=result["avatar_id"],
            image_url=f"data:image/png;base64,{result['image_data']}",
            timestamp=result["timestamp"],
            message="Avatar generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")


@router.post("/add-face", response_model=AvatarResponse)
async def add_face_to_avatar(request: AvatarFaceMapRequest):
    """
    Add a user's face to an existing avatar.
    
    Args:
        request: Request with avatar ID and face image
        
    Returns:
        Updated avatar with face
    """
    try:
        # Find avatar file
        avatar_files = [
            f for f in os.listdir(avatar_generator.storage_dir)
            if f.startswith(f"avatar_{request.avatar_id}")
        ]
        
        if not avatar_files:
            raise HTTPException(status_code=404, detail="Avatar not found")
        
        avatar_path = os.path.join(avatar_generator.storage_dir, avatar_files[0])
        
        # Extract face
        face_data = face_mapper.extract_face(request.face_image)
        
        if not face_data:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        # Add face overlay
        img_with_face = avatar_generator.add_face_overlay(
            avatar_path=avatar_path,
            face_image_base64=request.face_image
        )
        
        return AvatarResponse(
            success=True,
            avatar_id=request.avatar_id,
            image_url=f"data:image/png;base64,{img_with_face}",
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
            message="Face added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face mapping failed: {str(e)}")


@router.get("/{avatar_id}")
async def get_avatar(avatar_id: str):
    """
    Retrieve a generated avatar by ID.
    
    Args:
        avatar_id: Avatar unique identifier
        
    Returns:
        Avatar image data
    """
    try:
        # Find avatar file
        avatar_files = [
            f for f in os.listdir(avatar_generator.storage_dir)
            if f.startswith(f"avatar_{avatar_id}")
        ]
        
        if not avatar_files:
            raise HTTPException(status_code=404, detail="Avatar not found")
        
        avatar_path = os.path.join(avatar_generator.storage_dir, avatar_files[0])
        
        # Read and encode image
        import base64
        with open(avatar_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        
        return {
            "success": True,
            "avatar_id": avatar_id,
            "image_url": f"data:image/png;base64,{img_data}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving avatar: {str(e)}")
