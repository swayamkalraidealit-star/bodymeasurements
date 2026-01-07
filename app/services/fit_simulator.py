"""Garment fit simulation and analysis service."""
from typing import Dict, List, Tuple
from app.models.schemas import Measurements, FitZoneAnalysis
from app.models.garment_data import (
    FitZone, FitCategory, LengthCategory, GarmentSpec
)
from app.core.config import settings


class FitSimulator:
    """Simulate and analyze garment fit based on body measurements."""
    
    def __init__(self):
        """Initialize fit simulator with tolerance settings."""
        self.tol_perfect = settings.fit_tolerance_perfect
        self.tol_good = settings.fit_tolerance_good
        self.length_tol_perfect = settings.length_tolerance_perfect
        self.length_tol_acceptable = settings.length_tolerance_acceptable
    
    def analyze_fit(
        self,
        user_measurements: Measurements,
        garment_spec: GarmentSpec
    ) -> Dict:
        """
        Comprehensive fit analysis comparing user measurements to garment specs.
        
        Args:
            user_measurements: User's body measurements
            garment_spec: Garment size specifications
            
        Returns:
            Dict with overall_fit_score, zones analysis, and recommendations
        """
        zones_analysis = []
        zone_scores = []
        
        # Analyze each relevant measurement zone
        if user_measurements.shoulder_width and garment_spec.shoulder_width:
            zone_result = self._analyze_zone(
                FitZone.SHOULDERS,
                user_measurements.shoulder_width,
                garment_spec.shoulder_width,
                is_circumference=False
            )
            zones_analysis.append(zone_result)
            zone_scores.append(zone_result["fit_score"])
        
        if user_measurements.chest and garment_spec.chest:
            zone_result = self._analyze_zone(
                FitZone.CHEST,
                user_measurements.chest,
                garment_spec.chest,
                is_circumference=True
            )
            zones_analysis.append(zone_result)
            zone_scores.append(zone_result["fit_score"])
        
        if user_measurements.waist and garment_spec.waist:
            zone_result = self._analyze_zone(
                FitZone.WAIST,
                user_measurements.waist,
                garment_spec.waist,
                is_circumference=True
            )
            zones_analysis.append(zone_result)
            zone_scores.append(zone_result["fit_score"])
        
        if user_measurements.hip and garment_spec.hip:
            zone_result = self._analyze_zone(
                FitZone.HIPS,
                user_measurements.hip,
                garment_spec.hip,
                is_circumference=True
            )
            zones_analysis.append(zone_result)
            zone_scores.append(zone_result["fit_score"])
        
        if user_measurements.inseam and garment_spec.inseam:
            zone_result = self._analyze_length(
                FitZone.INSEAM,
                user_measurements.inseam,
                garment_spec.inseam
            )
            zones_analysis.append(zone_result)
            zone_scores.append(zone_result["fit_score"])
        
        # Calculate overall fit score
        overall_score = sum(zone_scores) / len(zone_scores) if zone_scores else 0
        overall_category = self._score_to_category(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(zones_analysis, overall_category)
        
        return {
            "overall_fit_score": round(overall_score, 2),
            "overall_fit_category": overall_category,
            "zones": zones_analysis,
            "recommendations": recommendations
        }
    
    def _analyze_zone(
        self,
        zone: FitZone,
        user_measurement: float,
        garment_measurement: float,
        is_circumference: bool = True
    ) -> Dict:
        """
        Analyze fit for a specific body zone.
        
        Args:
            zone: Body zone name
            user_measurement: User's measurement
            garment_measurement: Garment's measurement
            is_circumference: If True, treat as circumference (needs ease allowance)
            
        Returns:
            Zone analysis dict
        """
        # Add ease allowance for circumference measurements
        if is_circumference:
            # Garments should be 2-5% larger than body for comfortable fit
            ease_allowance = 0.03  # 3% ease
            ideal_garment_size = user_measurement * (1 + ease_allowance)
        else:
            ideal_garment_size = user_measurement
        
        # Calculate difference
        difference = garment_measurement - user_measurement
        relative_diff = abs(difference) / user_measurement
        
        # Determine fit category and score
        if is_circumference:
            fit_category, fit_score, description = self._categorize_circumference_fit(
                difference, relative_diff, zone
            )
        else:
            fit_category, fit_score, description = self._categorize_width_fit(
                difference, relative_diff, zone
            )
        
        # Generate recommendation
        recommendation = self._zone_recommendation(zone, fit_category, difference)
        
        return {
            "zone": zone.value,
            "user_measurement": round(user_measurement, 1),
            "garment_measurement": round(garment_measurement, 1),
            "difference": round(difference, 1),
            "fit_category": fit_category.value,
            "fit_score": round(fit_score, 2),
            "description": description,
            "recommendation": recommendation
        }
    
    def _categorize_circumference_fit(
        self,
        difference: float,
        relative_diff: float,
        zone: FitZone
    ) -> Tuple[FitCategory, float, str]:
        """Categorize fit for circumference measurements (chest, waist, hips)."""
        
        if -0.02 <= difference / 100 <= 0.05:  # -2% to +5% is perfect
            return (
                FitCategory.PERFECT_FIT,
                100.0,
                f"Perfect fit at {zone.value}. Garment provides ideal ease."
            )
        elif 0.05 < relative_diff <= 0.08:  # 5-8% difference is good
            if difference > 0:
                return (
                    FitCategory.SLIGHTLY_LOOSE,
                    85.0,
                    f"Slightly loose at {zone.value}. Still comfortable."
                )
            else:
                return (
                    FitCategory.SLIGHTLY_TIGHT,
                    80.0,
                    f"Slightly snug at {zone.value}. May feel fitted."
                )
        elif 0.08 < relative_diff <= 0.15:  # 8-15% difference
            if difference > 0:
                return (
                    FitCategory.LOOSE,
                    65.0,
                    f"Loose at {zone.value}. Consider sizing down."
                )
            else:
                return (
                    FitCategory.TIGHT,
                    60.0,
                    f"Tight at {zone.value}. May be uncomfortable."
                )
        else:  # >15% difference
            if difference > 0:
                return (
                    FitCategory.TOO_LOOSE,
                    40.0,
                    f"Too loose at {zone.value}. Definitely size down."
                )
            else:
                return (
                    FitCategory.TOO_TIGHT,
                    30.0,
                    f"Too tight at {zone.value}. Size up required."
                )
    
    def _categorize_width_fit(
        self,
        difference: float,
        relative_diff: float,
        zone: FitZone
    ) -> Tuple[FitCategory, float, str]:
        """Categorize fit for width measurements (shoulder width)."""
        
        if relative_diff <= 0.02:  # Within 2%
            return (
                FitCategory.PERFECT_FIT,
                100.0,
                f"Perfect fit at {zone.value}."
            )
        elif relative_diff <= 0.05:  # 2-5%
            if difference > 0:
                return (
                    FitCategory.SLIGHTLY_LOOSE,
                    85.0,
                    f"Slightly wide at {zone.value}."
                )
            else:
                return (
                    FitCategory.SLIGHTLY_TIGHT,
                    75.0,
                    f"Slightly narrow at {zone.value}. May pull."
                )
        elif relative_diff <= 0.10:  # 5-10%
            if difference > 0:
                return (
                    FitCategory.LOOSE,
                    65.0,
                    f"Too wide at {zone.value}. May droop."
                )
            else:
                return (
                    FitCategory.TIGHT,
                    50.0,
                    f"Too narrow at {zone.value}. Will pull uncomfortably."
                )
        else:  # >10%
            if difference > 0:
                return (
                    FitCategory.TOO_LOOSE,
                    40.0,
                    f"Much too wide at {zone.value}."
                )
            else:
                return (
                    FitCategory.TOO_TIGHT,
                    30.0,
                    f"Much too narrow at {zone.value}."
                )
    
    def _analyze_length(
        self,
        zone: FitZone,
        user_measurement: float,
        garment_measurement: float
    ) -> Dict:
        """Analyze length fit (inseam, sleeve, total length)."""
        difference = garment_measurement - user_measurement
        abs_diff = abs(difference)
        
        # Categorize length fit
        if abs_diff <= self.length_tol_perfect:  # Within 2cm
            fit_category = LengthCategory.PERFECT_LENGTH
            fit_score = 100.0
            description = f"Perfect length at {zone.value}."
        elif abs_diff <= self.length_tol_acceptable:  # 2-5cm
            if difference > 0:
                fit_category = LengthCategory.SLIGHTLY_LONG
                fit_score = 85.0
                description = f"Slightly long at {zone.value}. Can be hemmed."
            else:
                fit_category = LengthCategory.SLIGHTLY_SHORT
                fit_score = 80.0
                description = f"Slightly short at {zone.value}."
        elif abs_diff <= 10:  # 5-10cm
            if difference > 0:
                fit_category = LengthCategory.LONG
                fit_score = 65.0
                description = f"Long at {zone.value}. Hemming recommended."
            else:
                fit_category = LengthCategory.SHORT
                fit_score = 60.0
                description = f"Short at {zone.value}. May not cover properly."
        else:  # >10cm
            if difference > 0:
                fit_category = LengthCategory.TOO_LONG
                fit_score = 45.0
                description = f"Too long at {zone.value}. Significant alterations needed."
            else:
                fit_category = LengthCategory.TOO_SHORT
                fit_score = 40.0
                description = f"Too short at {zone.value}. Not recommended."
        
        recommendation = self._length_recommendation(zone, fit_category, difference)
        
        return {
            "zone": zone.value,
            "user_measurement": round(user_measurement, 1),
            "garment_measurement": round(garment_measurement, 1),
            "difference": round(difference, 1),
            "fit_category": fit_category.value,
            "fit_score": round(fit_score, 2),
            "description": description,
            "recommendation": recommendation
        }
    
    def _score_to_category(self, score: float) -> FitCategory:
        """Convert numerical score to fit category."""
        if score >= 95:
            return FitCategory.PERFECT_FIT
        elif score >= 80:
            return FitCategory.GOOD_FIT
        elif score >= 65:
            return FitCategory.SLIGHTLY_LOOSE
        elif score >= 50:
            return FitCategory.LOOSE
        else:
            return FitCategory.TOO_LOOSE
    
    def _zone_recommendation(
        self,
        zone: FitZone,
        fit_category: FitCategory,
        difference: float
    ) -> str:
        """Generate recommendation for a specific zone."""
        if fit_category in [FitCategory.PERFECT_FIT, FitCategory.GOOD_FIT]:
            return f"Excellent fit at {zone.value}!"
        elif fit_category in [FitCategory.SLIGHTLY_LOOSE, FitCategory.SLIGHTLY_TIGHT]:
            return f"Minor fit issue at {zone.value}, but still wearable."
        elif "LOOSE" in fit_category.value:
            return f"Consider sizing down for better fit at {zone.value}."
        elif "TIGHT" in fit_category.value:
            return f"Consider sizing up for comfort at {zone.value}."
        else:
            return "No specific recommendation."
    
    def _length_recommendation(
        self,
        zone: FitZone,
        length_category: LengthCategory,
        difference: float
    ) -> str:
        """Generate recommendation for length."""
        if "PERFECT" in length_category.value:
            return f"Perfect length at {zone.value}!"
        elif "LONG" in length_category.value and "TOO" not in length_category.value:
            return f"Can be hemmed to perfect length at {zone.value}."
        elif "SHORT" in length_category.value and "TOO" not in length_category.value:
            return f"Length is slightly short at {zone.value}, but acceptable."
        elif "TOO LONG" in length_category.value:
            return f"Significant hemming needed at {zone.value}."
        else:
            return f"Length at {zone.value} is not ideal for your measurements."
    
    def _generate_recommendations(
        self,
        zones_analysis: List[Dict],
        overall_category: FitCategory
    ) -> List[str]:
        """Generate overall fit recommendations."""
        recommendations = []
        
        # Check overall fit
        if overall_category == FitCategory.PERFECT_FIT:
            recommendations.append("✅ This size is a perfect fit for you!")
        elif overall_category == FitCategory.GOOD_FIT:
            recommendations.append("👍 This size fits well overall.")
        
        # Check individual problem zones
        tight_zones = [z for z in zones_analysis if "TIGHT" in z["fit_category"]]
        loose_zones = [z for z in zones_analysis if "LOOSE" in z["fit_category"]]
        
        if tight_zones and len(tight_zones) >= 2:
            zone_names = ", ".join([z["zone"] for z in tight_zones])
            recommendations.append(f"⚠️ Size up recommended due to tightness at: {zone_names}")
        
        if loose_zones and len(loose_zones) >= 2:
            zone_names = ", ".join([z["zone"] for z in loose_zones])
            recommendations.append(f"⚠️ Size down recommended due to looseness at: {zone_names}")
        
        # Check for specific alterations
        long_items = [z for z in zones_analysis if "LONG" in z["fit_category"]]
        if long_items:
            recommendations.append("✂️ Hemming may be needed to adjust length.")
        
        return recommendations


# Singleton instance
fit_simulator = FitSimulator()
