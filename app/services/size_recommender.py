"""Size recommendation service."""
import math
from typing import Dict, List, Optional, Tuple
from app.models.garment_specs import GarmentCategory, SizeChart, SizeChartDatabase, SizeSpecification


class SizeRecommendation:
    """Individual size recommendation with fit score."""
    
    def __init__(
        self,
        size: str,
        fit_score: float,
        measurements: Dict[str, float],
        fit_analysis: Dict[str, str]
    ):
        self.size = size
        self.fit_score = fit_score
        self.measurements = measurements
        self.fit_analysis = fit_analysis


class SizeRecommender:
    """Service for recommending garment sizes based on body measurements."""
    
    def __init__(self):
        self.db = SizeChartDatabase()
        
        # Measurement weights for scoring (total = 100)
        self.weights = {
            'chest': 35,
            'waist': 30,
            'hip': 25,
            'shoulder_width': 5,
            'inseam': 5,
            'height': 5
        }
        
        # Tolerance in cm (±this amount is acceptable)
        self.tolerance = {
            'chest': 3,
            'waist': 3,
            'hip': 3,
            'shoulder_width': 2,
            'inseam': 5,
            'height': 10
        }
    
    def recommend_sizes(
        self,
        user_measurements: Dict[str, float],
        category: GarmentCategory,
        top_n: int = 3
    ) -> List[SizeRecommendation]:
        """
        Recommend sizes for a garment category.
       
        Args:
            user_measurements: Dictionary of user measurements in cm
            category: Garment category
            top_n: Number of recommendations to return
            
        Returns:
            List of SizeRecommendation objects, sorted by fit score
        """
        size_chart = self.db.get_size_chart(category)
        
        if not size_chart:
            return []
        
        recommendations = []
        
        for size_name, size_spec in size_chart.sizes.items():
            fit_score, fit_analysis = self._calculate_fit_score(
                user_measurements,
                size_spec
            )
            
            recommendations.append(SizeRecommendation(
                size=size_name,
                fit_score=fit_score,
                measurements=size_spec.dict(exclude_none=True),
                fit_analysis=fit_analysis
            ))
        
        # Sort by fit score (descending)
        recommendations.sort(key=lambda x: x.fit_score, reverse=True)
        
        return recommendations[:top_n]
    
    def _calculate_fit_score(
        self,
        user_measurements: Dict[str, float],
        size_spec: SizeSpecification
    ) -> Tuple[float, Dict[str, str]]:
        """
        Calculate fit score for a specific size.
        
        Returns:
            Tuple of (fit_score, fit_analysis)
            - fit_score: 0-100, higher is better
            - fit_analysis: Dictionary explaining fit for each measurement
        """
        total_score = 0
        total_weight = 0
        fit_analysis = {}
        
        # Compare each measurement
        for measurement_name, user_value in user_measurements.items():
            if user_value is None:
                continue
            
            # Get garment spec value
            garment_value = getattr(size_spec, measurement_name, None)
            
            if garment_value is None:
                continue
            
            # Special handling for height_range
            if measurement_name == 'height' and size_spec.height_range:
                min_height, max_height = size_spec.height_range
                range_center = (min_height + max_height) / 2
                
                if min_height <= user_value <= max_height:
                    # Within range - score based on distance from center
                    # Perfect 100 at center, decreasing to 95 at edges
                    range_span = max_height - min_height
                    distance_from_center = abs(user_value - range_center)
                    score = 100 - (distance_from_center / (range_span / 2)) * 5
                    fit_analysis['height'] = "Perfect fit"
                else:
                    # Calculate how far outside range
                    if user_value < min_height:
                        diff = min_height - user_value
                        score = max(0, 100 - (diff / self.tolerance['height']) * 50)
                        fit_analysis['height'] = f"{diff:.0f}cm shorter than recommended"
                    else:
                        diff = user_value - max_height
                        score = max(0, 100 - (diff / self.tolerance['height']) * 50)
                        fit_analysis['height'] = f"{diff:.0f}cm taller than recommended"
            else:
                # Regular measurement comparison
                diff = abs(user_value - garment_value)
                tolerance = self.tolerance.get(measurement_name, 3)
                
                if diff <= tolerance:
                    # Within tolerance - score decreases as diff increases
                    # Perfect 100 at 0cm diff, decreasing to 90 at tolerance edge
                    # This ensures closer matches get higher scores
                    score = 100 - (diff / tolerance) * 10
                    
                    # More nuanced fit analysis
                    if diff == 0:
                        fit_analysis[measurement_name] = "Perfect fit"
                    elif diff < tolerance * 0.33:  # Very close (within 1cm for 3cm tolerance)
                        fit_analysis[measurement_name] = "Excellent fit"
                    elif diff < tolerance * 0.67:  # Close (within 2cm for 3cm tolerance)
                        fit_analysis[measurement_name] = "Great fit"
                    else:  # Within tolerance but on the edge
                        if user_value > garment_value:
                            fit_analysis[measurement_name] = f"Good fit (snug)"
                        else:
                            fit_analysis[measurement_name] = f"Good fit (relaxed)"
                else:
                    # Outside tolerance - calculate penalty
                    excess = diff - tolerance
                    score = max(0, 100 - (excess / tolerance) * 50)
                    
                    if user_value > garment_value:
                        fit_analysis[measurement_name] = f"May be {diff:.0f}cm tight"
                    else:
                        fit_analysis[measurement_name] = f"May be {diff:.0f}cm loose"
            
            # Apply weight
            weight = self.weights.get(measurement_name, 0)
            total_score += score * weight
            total_weight += weight
        
        # Calculate final score
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0
        
        return round(final_score, 1), fit_analysis
    
    def get_fit_category(self, fit_score: float) -> str:
        """Get human-readable fit category."""
        if fit_score >= 90:
            return "Perfect Fit"
        elif fit_score >= 75:
            return "Great Fit"
        elif fit_score >= 60:
            return "Good Fit"
        elif fit_score >= 45:
            return "Acceptable"
        else:
            return "Poor Fit"
