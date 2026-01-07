"""API routes for garment fit analysis."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    FitAnalysisRequest,
    FitAnalysisResponse,
    SizeRecommendRequest,
    GarmentInfoResponse
)
from app.services.fit_simulator import fit_simulator
from app.models.garment_data import GarmentSpec, GarmentAsset, GarmentCategory
from typing import List, Dict

router = APIRouter()

# Sample garment data (in production, this would come from a database)
SAMPLE_GARMENTS: Dict[str, GarmentAsset] = {
    "tshirt_basic_001": GarmentAsset(
        id="tshirt_basic_001",
        name="Basic Cotton T-Shirt",
        category=GarmentCategory.TSHIRT,
        asset_path="static/clothing_assets/shirts/tshirt_basic_001.png",
        sizes=[
            GarmentSpec(
                size="S",
                shoulder_width=42.0,
                chest=92.0,
                waist=88.0,
                total_length=68.0
            ),
            GarmentSpec(
                size="M",
                shoulder_width=45.0,
                chest=98.0,
                waist=94.0,
                total_length=70.0
            ),
            GarmentSpec(
                size="L",
                shoulder_width=48.0,
                chest=104.0,
                waist=100.0,
                total_length=72.0
            ),
            GarmentSpec(
                size="XL",
                shoulder_width=51.0,
                chest=110.0,
                waist=106.0,
                total_length=74.0
            ),
        ]
    ),
    "jeans_slim_001": GarmentAsset(
        id="jeans_slim_001",
        name="Slim Fit Jeans",
        category=GarmentCategory.MENS_PANTS,
        asset_path="static/clothing_assets/pants/jeans_001.png",
        sizes=[
            GarmentSpec(
                size="30",
                waist=76.2,
                hip=94.0,
                inseam=81.0
            ),
            GarmentSpec(
                size="32",
                waist=81.3,
                hip=99.0,
                inseam=81.0
            ),
            GarmentSpec(
                size="34",
                waist=86.4,
                hip=104.0,
                inseam=81.0
            ),
            GarmentSpec(
                size="36",
                waist=91.4,
                hip=109.0,
                inseam=81.0
            ),
        ]
    )
}


@router.post("/analyze", response_model=FitAnalysisResponse)
async def analyze_garment_fit(request: FitAnalysisRequest):
    """
    Analyze how a garment fits based on user measurements.
    
    Args:
        request: Fit analysis request with measurements and garment info
        
    Returns:
        Detailed fit analysis with zone-by-zone breakdown
    """
    try:
        # Get garment
        garment = SAMPLE_GARMENTS.get(request.garment_id)
        if not garment:
            raise HTTPException(status_code=404, detail="Garment not found")
        
        # Find requested size
        garment_spec = next(
            (s for s in garment.sizes if s.size == request.garment_size),
            None
        )
        if not garment_spec:
            raise HTTPException(status_code=404, detail=f"Size {request.garment_size} not available")
        
        # Perform fit analysis
        analysis = fit_simulator.analyze_fit(
            user_measurements=request.measurements,
            garment_spec=garment_spec
        )
        
        # Analyze alternative sizes
        alternative_sizes = []
        for spec in garment.sizes:
            if spec.size != request.garment_size:
                alt_analysis = fit_simulator.analyze_fit(
                    user_measurements=request.measurements,
                    garment_spec=spec
                )
                alternative_sizes.append({
                    "size": spec.size,
                    "fit_score": alt_analysis["overall_fit_score"],
                    "fit_category": alt_analysis["overall_fit_category"].value
                })
        
        # Sort alternatives by fit score
        alternative_sizes.sort(key=lambda x: x["fit_score"], reverse=True)
        
        return FitAnalysisResponse(
            success=True,
            overall_fit_score=analysis["overall_fit_score"],
            overall_fit_category=analysis["overall_fit_category"],
            zones=analysis["zones"],
            recommendations=analysis["recommendations"],
            alternative_sizes=alternative_sizes[:3],  # Top 3 alternatives
            message=f"Fit analysis completed for {garment.name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fit analysis failed: {str(e)}")


@router.post("/recommend-size")
async def recommend_size(request: SizeRecommendRequest):
    """
    Recommend the best size for a garment based on user measurements.
    
    Args:
        request: Size recommendation request
        
    Returns:
        Recommended size with fit analysis
    """
    try:
        # Get garment
        garment = SAMPLE_GARMENTS.get(request.garment_id)
        if not garment:
            raise HTTPException(status_code=404, detail="Garment not found")
        
        # Analyze all sizes
        size_scores = []
        for spec in garment.sizes:
            analysis = fit_simulator.analyze_fit(
                user_measurements=request.measurements,
                garment_spec=spec
            )
            size_scores.append({
                "size": spec.size,
                "fit_score": analysis["overall_fit_score"],
                "fit_category": analysis["overall_fit_category"].value,
                "zones": analysis["zones"],
                "recommendations": analysis["recommendations"]
            })
        
        # Sort by fit score
        size_scores.sort(key=lambda x: x["fit_score"], reverse=True)
        
        # Return best fit
        best_fit = size_scores[0]
        
        return {
            "success": True,
            "garment_name": garment.name,
            "recommended_size": best_fit["size"],
            "fit_score": best_fit["fit_score"],
            "fit_category": best_fit["fit_category"],
            "analysis": best_fit,
            "alternative_sizes": size_scores[1:4],  # Next 3 best options
            "message": f"Recommended size {best_fit['size']} for best fit"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Size recommendation failed: {str(e)}")


@router.get("/garments", response_model=GarmentInfoResponse)
async def list_garments(category: str = None):
    """
    List available garments for try-on and fit analysis.
    
    Args:
        category: Optional filter by garment category
        
    Returns:
        List of available garments
    """
    try:
        garments = list(SAMPLE_GARMENTS.values())
        
        # Filter by category if specified
        if category:
            garments = [g for g in garments if g.category.value == category]
        
        garments_data = [
            {
                "id": g.id,
                "name": g.name,
                "category": g.category.value,
                "available_sizes": [s.size for s in g.sizes],
                "thumbnail": g.thumbnail_path or g.asset_path
            }
            for g in garments
        ]
        
        return GarmentInfoResponse(
            garments=garments_data,
            total_count=len(garments_data)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list garments: {str(e)}")
