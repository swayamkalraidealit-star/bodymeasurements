"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class LandmarkData(BaseModel):
    """3D landmark coordinates."""
    x: float = Field(..., description="Normalized x coordinate (0-1)")
    y: float = Field(..., description="Normalized y coordinate (0-1)")
    z: float = Field(..., description="Normalized z coordinate (depth)")
    visibility: float = Field(..., description="Landmark visibility (0-1)")


class MeasurementRequest(BaseModel):
    """Request model for body measurements."""
    front_image: str = Field(..., description="Base64 encoded front view image")
    side_image: Optional[str] = Field(None, description="Base64 encoded side view image")
    calibration_height: float = Field(..., description="Actual height in cm for calibration", gt=0)
    units: str = Field("metric", description="Units: 'metric' (cm) or 'imperial' (inches)")


class Measurements(BaseModel):
    """Body measurements."""
    shoulder_width: Optional[float] = Field(None, description="Shoulder width")
    chest: Optional[float] = Field(None, description="Chest circumference")
    waist: Optional[float] = Field(None, description="Waist circumference")
    hip: Optional[float] = Field(None, description="Hip circumference")
    height: Optional[float] = Field(None, description="Total height")
    inseam: Optional[float] = Field(None, description="Inseam length")
    units: str = Field("cm", description="Measurement units")


class MeasurementResponse(BaseModel):
    """Response model for measurements."""
    success: bool = Field(..., description="Whether measurement was successful")
    measurements: Optional[Measurements] = Field(None, description="Body measurements")
    landmarks_detected: bool = Field(..., description="Whether pose landmarks were detected")
    confidence_score: Optional[float] = Field(None, description="Average detection confidence (0-1)")
    message: Optional[str] = Field(None, description="Any additional information or errors")
    front_landmarks: Optional[List[LandmarkData]] = Field(None, description="Front view landmarks")
    side_landmarks: Optional[List[LandmarkData]] = Field(None, description="Side view landmarks")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


# Size Recommendation Schemas

class SizeRecommendationRequest(BaseModel):
    """Request for size recommendations."""
    measurements: Measurements = Field(..., description="User body measurements")
    garment_category: str = Field(..., description="Garment category (MENS_SHIRT, WOMENS_TOP, etc.)")


class SizeFitAnalysis(BaseModel):
    """Fit analysis for individual measurements."""
    measurement: str = Field(..., description="Measurement name")
    analysis: str = Field(..., description="Fit description")


class SingleSizeRecommendation(BaseModel):
    """Single size recommendation."""
    size: str = Field(..., description="Size name (XS, S, M, L, XL, or numeric)")
    fit_score: float = Field(..., description="Fit score 0-1, higher is better (multiply by 100 for percentage)")
    fit_category: str = Field(..., description="Fit category (Perfect Fit, Great Fit, etc.)")
    measurements: Dict[str, float] = Field(..., description="Garment measurements for this size")
    fit_analysis: List[SizeFitAnalysis] = Field(..., description="Detailed fit analysis")


class SizeRecommendationResponse(BaseModel):
    """Response with size recommendations."""
    success: bool = Field(..., description="Whether recommendation was successful")
    garment_category: str = Field(..., description="Garment category")
    garment_name: str = Field(..., description="Human-readable garment name")
    recommendations: List[SingleSizeRecommendation] = Field(..., description="Recommended sizes")
    message: Optional[str] = Field(None, description="Any additional information")


class GarmentCategoryInfo(BaseModel):
    """Information about a garment category."""
    key: str = Field(..., description="Category key")
    name: str = Field(..., description="Human-readable name")
