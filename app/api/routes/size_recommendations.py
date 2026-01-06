"""API routes for size recommendations."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    SizeRecommendationRequest,
    SizeRecommendationResponse,
    SingleSizeRecommendation,
    SizeFitAnalysis,
    GarmentCategoryInfo,
    HealthResponse
)
from app.models.garment_specs import GarmentCategory, SizeChartDatabase
from app.services.size_recommender import SizeRecommender
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
size_recommender = SizeRecommender()
size_chart_db = SizeChartDatabase()


@router.post("/recommend", response_model=SizeRecommendationResponse)
async def get_size_recommendations(request: SizeRecommendationRequest):
    """
    Get size recommendations based on body measurements.
    
    Args:
        request: SizeRecommendationRequest with measurements and garment category
        
    Returns:
        SizeRecommendationResponse with recommended sizes
    """
    try:
        logger.info(f"Getting size recommendations for {request.garment_category}")
        
        # Validate garment category
        try:
            category = GarmentCategory(request.garment_category)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid garment category: {request.garment_category}"
            )
        
        # Get size chart
        size_chart = size_chart_db.get_size_chart(category)
        if not size_chart:
            raise HTTPException(
                status_code=404,
                detail=f"Size chart not found for category: {request.garment_category}"
            )
        
        # Convert measurements to dict
        measurements_dict = request.measurements.dict(exclude={'units'}, exclude_none=True)
        
        # Get recommendations
        recommendations = size_recommender.recommend_sizes(
            user_measurements=measurements_dict,
            category=category,
            top_n=3
        )
        
        if not recommendations:
            return SizeRecommendationResponse(
                success=False,
                garment_category=request.garment_category,
                garment_name=size_chart.name,
                recommendations=[],
                message="Unable to generate size recommendations"
            )
        
        # Convert to response format
        recommendation_list = []
        for rec in recommendations:
            fit_analysis_list = [
                SizeFitAnalysis(measurement=key, analysis=value)
                for key, value in rec.fit_analysis.items()
            ]
            
            # Filter out height_range from measurements (it's a tuple, not a float)
            measurements_dict = {
                k: v for k, v in rec.measurements.items() 
                if k != 'height_range' and isinstance(v, (int, float))
            }
            
            recommendation_list.append(SingleSizeRecommendation(
                size=rec.size,
                fit_score=rec.fit_score / 100.0,  # Normalize to 0-1 range
                fit_category=size_recommender.get_fit_category(rec.fit_score),
                measurements=measurements_dict,
                fit_analysis=fit_analysis_list
            ))
        
        logger.info(f"Generated {len(recommendation_list)} recommendations")
        
        return SizeRecommendationResponse(
            success=True,
            garment_category=request.garment_category,
            garment_name=size_chart.name,
            recommendations=recommendation_list,
            message="Size recommendations generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating size recommendations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/categories", response_model=list[GarmentCategoryInfo])
async def get_garment_categories():
    """Get list of available garment categories."""
    try:
        categories = size_chart_db.get_all_categories()
        return categories
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/size-chart/{category}")
async def get_size_chart(category: str):
    """Get size chart for a specific garment category."""
    try:
        # Validate category
        try:
            cat_enum = GarmentCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid garment category: {category}"
            )
        
        # Get size chart
        size_chart = size_chart_db.get_size_chart(cat_enum)
        if not size_chart:
            raise HTTPException(
                status_code=404,
                detail=f"Size chart not found for category: {category}"
            )
        
        return {
            "category": category,
            "name": size_chart.name,
            "sizes": size_chart.sizes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching size chart: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
