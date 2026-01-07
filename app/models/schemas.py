"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from app.models.garment_data import SkinTone, FitZone, FitCategory, LengthCategory


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
    gender: str = Field("male", description="Gender: 'male' or 'female' for body proportion calculations")


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


# Avatar Generation Schemas

class AvatarGenerateRequest(BaseModel):
    """Request to generate a 2D avatar."""
    measurements: Measurements = Field(..., description="User body measurements")
    skin_tone: SkinTone = Field(SkinTone.MEDIUM, description="Skin tone selection")
    gender: str = Field("neutral", description="Gender: male, female, neutral")
    face_image: Optional[str] = Field(None, description="Base64 encoded face image for mapping")


class AvatarResponse(BaseModel):
    """Response with generated avatar."""
    success: bool = Field(..., description="Whether avatar generation was successful")
    avatar_id: str = Field(..., description="Unique avatar identifier")
    image_url: str = Field(..., description="URL or base64 of avatar image")
    timestamp: str = Field(..., description="Generation timestamp")
    message: Optional[str] = Field(None, description="Any additional information")


class AvatarFaceMapRequest(BaseModel):
    """Request to add face to avatar."""
    avatar_id: str = Field(..., description="Avatar ID to update")
    face_image: str = Field(..., description="Base64 encoded face image")


# Virtual Try-On Schemas

class TryOnRequest(BaseModel):
    """Request to simulate clothing on avatar."""
    avatar_id: str = Field(..., description="Avatar ID")
    garment_id: str = Field(..., description="Garment asset ID")
    garment_size: str = Field(..., description="Size to try on (XS, S, M, L, XL)")


class TryOnResponse(BaseModel):
    """Response with try-on result."""
    success: bool = Field(..., description="Whether try-on was successful")
    tryon_image: str = Field(..., description="Base64 or URL of avatar wearing garment")
    garment_info: Dict[str, Any] = Field(..., description="Garment information")
    message: Optional[str] = Field(None, description="Any additional information")


class MultipleTryOnRequest(BaseModel):
    """Request to try multiple garments."""
    avatar_id: str = Field(..., description="Avatar ID")
    garment_configs: List[Dict[str, str]] = Field(
        ..., 
        description="List of {garment_id, size} configs"
    )


# Fit Analysis Schemas

class FitZoneAnalysis(BaseModel):
    """Detailed fit analysis for a single zone."""
    zone: FitZone = Field(..., description="Body zone name")
    user_measurement: float = Field(..., description="User's measurement for this zone")
    garment_measurement: float = Field(..., description="Garment's measurement for this zone")
    difference: float = Field(..., description="Difference (user - garment)")
    fit_category: FitCategory = Field(..., description="Fit quality category")
    fit_score: float = Field(..., description="Fit score 0-100, higher is better")
    description: str = Field(..., description="Human-readable fit description")
    recommendation: Optional[str] = Field(None, description="Recommendation for this zone")


class FitAnalysisRequest(BaseModel):
    """Request for garment fit analysis."""
    measurements: Measurements = Field(..., description="User body measurements")
    garment_id: str = Field(..., description="Garment to analyze")
    garment_size: str = Field(..., description="Size to analyze")


class FitAnalysisResponse(BaseModel):
    """Response with complete fit analysis."""
    success: bool = Field(..., description="Whether analysis was successful")
    overall_fit_score: float = Field(..., description="Overall fit score 0-100")
    overall_fit_category: FitCategory = Field(..., description="Overall fit category")
    zones: List[FitZoneAnalysis] = Field(..., description="Zone-by-zone analysis")
    recommendations: List[str] = Field(default_factory=list, description="General recommendations")
    alternative_sizes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Suggested alternative sizes with scores"
    )
    message: Optional[str] = Field(None, description="Any additional information")


class SizeRecommendRequest(BaseModel):
    """Request for size recommendation."""
    measurements: Measurements = Field(..., description="User body measurements")
    garment_id: str = Field(..., description="Garment ID")


class GarmentInfoResponse(BaseModel):
    """Response with available garment information."""
    garments: List[Dict[str, Any]] = Field(..., description="List of available garments")
    total_count: int = Field(..., description="Total number of garments")
