"""API routes for virtual try-on."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import TryOnRequest, TryOnResponse, MultipleTryOnRequest
from app.services.clothing_overlay import clothing_overlay
from app.services.avatar_generator import avatar_generator
import os
import base64

router = APIRouter()


@router.post("/simulate", response_model=TryOnResponse)
async def simulate_tryon(request: TryOnRequest):
    """
    Simulate clothing on an avatar.
    
    Args:
        request: Try-on request with avatar ID and garment info
        
    Returns:
        Avatar image wearing the specified garment
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
        
        # Load avatar and encode to base64
        with open(avatar_path, "rb") as f:
            avatar_base64 = base64.b64encode(f.read()).decode()
        
        # Overlay garment
        tryon_image = clothing_overlay.overlay_garment(
            avatar_image_base64=avatar_base64,
            garment_id=request.garment_id,
            scale_factor=1.0
        )
        
        return TryOnResponse(
            success=True,
            tryon_image=f"data:image/png;base64,{tryon_image}",
            garment_info={
                "garment_id": request.garment_id,
                "size": request.garment_size
            },
            message="Try-on simulation completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Try-on simulation failed: {str(e)}")


@router.post("/multiple")
async def simulate_multiple_tryon(request: MultipleTryOnRequest):
    """
    Try on multiple garments at once (layering).
    
    Args:
        request: Multiple try-on request with avatar ID and garment list
        
    Returns:
        Avatar with multiple garments overlaid
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
        
        # Load avatar
        with open(avatar_path, "rb") as f:
            current_image = base64.b64encode(f.read()).decode()
        
        # Overlay each garment in sequence
        for garment_config in request.garment_configs:
            current_image = clothing_overlay.overlay_garment(
                avatar_image_base64=current_image,
                garment_id=garment_config["garment_id"],
                scale_factor=1.0
            )
        
        return {
            "success": True,
            "tryon_image": f"data:image/png;base64,{current_image}",
            "garments_applied": len(request.garment_configs),
            "message": "Multiple garment try-on completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple try-on failed: {str(e)}")


@router.get("/garments")
async def list_available_garments():
    """
    List all available garments for try-on.
    
    Returns:
        List of garment IDs and metadata
    """
    # Sample garment list (in production, load from database/filesystem)
    garments = [
        {
            "id": "tshirt_basic_001",
            "name": "Basic T-Shirt",
            "category": "TSHIRT",
            "colors": ["blue", "black", "white"]
        },
        {
            "id": "jeans_slim_001",
            "name": "Slim Fit Jeans",
            "category": "PANTS",
            "colors": ["blue", "black"]
        }
    ]
    
    return {
        "success": True,
        "garments": garments,
        "total_count": len(garments)
    }
