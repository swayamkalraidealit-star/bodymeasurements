"""Data models for garment and clothing specifications."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class GarmentCategory(str, Enum):
    """Garment categories."""
    MENS_SHIRT = "MENS_SHIRT"
    WOMENS_TOP = "WOMENS_TOP"
    MENS_PANTS = "MENS_PANTS"
    WOMENS_PANTS = "WOMENS_PANTS"
    DRESS = "DRESS"
    JACKET = "JACKET"
    TSHIRT = "TSHIRT"


class FitZone(str, Enum):
    """Body fit zones for garment fitting analysis."""
    SHOULDERS = "shoulders"
    CHEST = "chest"
    SLEEVES = "sleeves"
    WAIST = "waist"
    HIPS = "hips"
    INSEAM = "inseam"
    LENGTH = "length"


class FitCategory(str, Enum):
    """Fit quality categories."""
    PERFECT_FIT = "Perfect Fit"
    GOOD_FIT = "Good Fit"
    SLIGHTLY_LOOSE = "Slightly Loose"
    LOOSE = "Loose"
    TOO_LOOSE = "Too Loose"
    SLIGHTLY_TIGHT = "Slightly Tight"
    TIGHT = "Tight"
    TOO_TIGHT = "Too Tight"


class LengthCategory(str, Enum):
    """Length fit categories."""
    PERFECT_LENGTH = "Perfect Length"
    SLIGHTLY_SHORT = "Slightly Short"
    SHORT = "Short"
    TOO_SHORT = "Too Short"
    SLIGHTLY_LONG = "Slightly Long"
    LONG = "Long"
    TOO_LONG = "Too Long"


class AnchorPoint(BaseModel):
    """Anchor point for clothing overlay positioning."""
    landmark_index: int = Field(..., description="MediaPipe landmark index")
    offset_x: float = Field(0.0, description="X offset in pixels")
    offset_y: float = Field(0.0, description="Y offset in pixels")
    description: str = Field(..., description="Description of anchor point")


class GarmentSpec(BaseModel):
    """Garment size specifications."""
    size: str = Field(..., description="Size label (XS, S, M, L, XL or numeric)")
    shoulder_width: Optional[float] = Field(None, description="Shoulder width in cm")
    chest: Optional[float] = Field(None, description="Chest circumference in cm")
    waist: Optional[float] = Field(None, description="Waist circumference in cm")
    hip: Optional[float] = Field(None, description="Hip circumference in cm")
    sleeve_length: Optional[float] = Field(None, description="Sleeve length in cm")
    total_length: Optional[float] = Field(None, description="Total garment length in cm")
    inseam: Optional[float] = Field(None, description="Inseam length in cm")


class GarmentAsset(BaseModel):
    """Garment asset information."""
    id: str = Field(..., description="Unique garment ID")
    name: str = Field(..., description="Garment display name")
    category: GarmentCategory = Field(..., description="Garment category")
    asset_path: str = Field(..., description="Path to garment image asset")
    thumbnail_path: Optional[str] = Field(None, description="Path to thumbnail image")
    sizes: List[GarmentSpec] = Field(..., description="Available sizes and specs")
    anchor_points: Dict[str, AnchorPoint] = Field(
        default_factory=dict,
        description="Anchor points for overlay positioning"
    )
    fit_zones: List[FitZone] = Field(
        default_factory=list,
        description="Relevant fit zones for this garment"
    )
    description: Optional[str] = Field(None, description="Garment description")


class SkinTone(str, Enum):
    """Available skin tone options."""
    LIGHT = "light"
    MEDIUM_LIGHT = "medium_light"
    MEDIUM = "medium"
    MEDIUM_DARK = "medium_dark"
    DARK = "dark"


class AvatarTemplate(BaseModel):
    """Avatar body template configuration."""
    gender: str = Field(..., description="Gender: male, female, neutral")
    base_height: float = Field(170.0, description="Base height in cm for template")
    component_paths: Dict[str, str] = Field(
        ..., 
        description="Paths to avatar component images (head, torso, arms, legs)"
    )
    scaling_ratios: Dict[str, float] = Field(
        default_factory=dict,
        description="Default scaling ratios for components"
    )
    landmark_mappings: Dict[str, List[int]] = Field(
        default_factory=dict,
        description="Maps body parts to MediaPipe landmark indices"
    )
