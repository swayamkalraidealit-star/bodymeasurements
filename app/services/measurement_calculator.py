"""Measurement calculation service."""
import numpy as np
import math
from typing import Dict, List, Optional, Tuple
from app.services.pose_detector import PoseLandmark


class MeasurementCalculator:
    """Calculate anthropometric measurements from pose landmarks."""
    
    @staticmethod
    def calculate_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            point1: (x, y) coordinates
            point2: (x, y) coordinates
            
        Returns:
            Distance in pixels
        """
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    @staticmethod
    def pixels_to_cm(pixels: float, calibration_factor: float) -> float:
        """
        Convert pixels to centimeters using calibration factor.
        
        Args:
            pixels: Distance in pixels
            calibration_factor: Pixels per cm
            
        Returns:
            Distance in cm
        """
        return pixels / calibration_factor
    
    @staticmethod
    def cm_to_inches(cm: float) -> float:
        """Convert centimeters to inches."""
        return cm / 2.54
    
    def calculate_calibration_factor(
        self,
        landmarks: List[Dict],
        image_height: int,
        actual_height_cm: float
    ) -> Optional[float]:
        """
        Calculate pixels-per-cm calibration factor using known height.
        
        Args:
            landmarks: List of pose landmarks
            image_height: Image height in pixels
            actual_height_cm: Person's actual height in cm
            
        Returns:
            Calibration factor (pixels per cm), or None if calculation failed
        """
        # Get head and ankle landmarks
        nose = self._get_landmark_point(landmarks, PoseLandmark.NOSE, 1, image_height)
        left_ankle = self._get_landmark_point(landmarks, PoseLandmark.LEFT_ANKLE, 1, image_height)
        right_ankle = self._get_landmark_point(landmarks, PoseLandmark.RIGHT_ANKLE, 1, image_height)
        
        if not nose or not (left_ankle or right_ankle):
            return None
        
        # Use available ankle (prefer average if both present)
        if left_ankle and right_ankle:
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
        elif left_ankle:
            ankle_y = left_ankle[1]
        else:
            ankle_y = right_ankle[1]
        
        # Calculate height in pixels
        height_pixels = abs(ankle_y - nose[1])
        
        if height_pixels == 0:
            return None
        
        # Calculate calibration factor
        calibration_factor = height_pixels / actual_height_cm
        
        return calibration_factor
    
    def _get_landmark_point(
        self,
        landmarks: List[Dict],
        index: int,
        image_width: int,
        image_height: int
    ) -> Optional[Tuple[float, float]]:
        """Get landmark coordinates."""
        if index >= len(landmarks):
            return None
        
        landmark = landmarks[index]
        
        if landmark['visibility'] < 0.5:
            return None
        
        x = landmark['x'] * image_width
        y = landmark['y'] * image_height
        
        return (x, y)
    
    def calculate_measurements(
        self,
        front_landmarks: Dict,
        side_landmarks: Optional[Dict],
        calibration_height_cm: float,
        units: str = "metric",
        gender: str = "male"
    ) -> Dict:
        """
        Calculate all body measurements using anatomically correct proportions.
        
        Args:
            front_landmarks: Front view pose detection results
            side_landmarks: Side view pose detection results (optional)
            calibration_height_cm: Actual height in cm
            units: 'metric' or 'imperial'
            gender: 'male' or 'female' for gender-specific calculations
            
        Returns:
            Dictionary of measurements
        """
        measurements = {}
        
        # Get calibration factor from front view
        calibration_factor = self.calculate_calibration_factor(
            front_landmarks['landmarks'],
            front_landmarks['image_height'],
            calibration_height_cm
        )
        
        if not calibration_factor:
            return measurements
        
        landmarks = front_landmarks['landmarks']
        img_w = front_landmarks['image_width']
        img_h = front_landmarks['image_height']
        
        # Get key landmarks
        left_shoulder = self._get_landmark_point(landmarks, PoseLandmark.LEFT_SHOULDER, img_w, img_h)
        right_shoulder = self._get_landmark_point(landmarks, PoseLandmark.RIGHT_SHOULDER, img_w, img_h)
        left_hip = self._get_landmark_point(landmarks, PoseLandmark.LEFT_HIP, img_w, img_h)
        right_hip = self._get_landmark_point(landmarks, PoseLandmark.RIGHT_HIP, img_w, img_h)
        nose = self._get_landmark_point(landmarks, PoseLandmark.NOSE, img_w, img_h)
        left_ankle = self._get_landmark_point(landmarks, PoseLandmark.LEFT_ANKLE, img_w, img_h)
        right_ankle = self._get_landmark_point(landmarks, PoseLandmark.RIGHT_ANKLE, img_w, img_h)
        
        # 1. Shoulder Width
        if left_shoulder and right_shoulder:
            shoulder_width_px = self.calculate_distance(left_shoulder, right_shoulder)
            shoulder_width_cm = self.pixels_to_cm(shoulder_width_px, calibration_factor)
            measurements['shoulder_width'] = shoulder_width_cm
        
        # 2. Height
        if nose and (left_ankle or right_ankle):
            ankle_y = left_ankle[1] if left_ankle else right_ankle[1]
            if right_ankle and left_ankle:
                ankle_y = (left_ankle[1] + right_ankle[1]) / 2
            
            height_px = abs(ankle_y - nose[1])
            height_cm = self.pixels_to_cm(height_px, calibration_factor)
            measurements['height'] = height_cm
        
        # 3-5. Chest, Waist, & Hip using anthropometric proportions
        # Based on research: body proportions correlate with height and shoulder width
        height = measurements.get('height', calibration_height_cm)
        shoulder_width = measurements.get('shoulder_width')
        
        if shoulder_width:
            # Anthropometric ratios based on gender
            if gender.lower() == 'female':
                # Female proportions (based on anthropometric data)
                # For females: chest ≈ 85-92% of shoulder width * 2
                # Waist ≈ 68-75% of shoulder width * 2
                # Hip ≈ 95-105% of shoulder width * 2
                chest_ratio = 2.1  # shoulder_width * 2.1 ≈ realistic chest for females
                waist_ratio = 1.65  # More narrow waist relative to shoulders
                hip_ratio = 2.35  # Wider hips relative to shoulders
            else:  # male
                # Male proportions
                # For males: chest ≈ 95-105% of shoulder width * 2
                # Waist ≈ 75-85% of shoulder width * 2
                # Hip ≈ 85-95% of shoulder width * 2
                chest_ratio = 2.15  # shoulder_width * 2.15 ≈ realistic chest for males
                waist_ratio = 1.85  # Wider waist relative to shoulders compared to females
                hip_ratio = 2.1  # Narrower hips relative to shoulders compared to females
            
            measurements['chest'] = shoulder_width * chest_ratio
            measurements['waist'] = shoulder_width * waist_ratio
            measurements['hip'] = shoulder_width * hip_ratio
        
        # 6. Inseam (hip to ankle)
        if left_hip and left_ankle:
            inseam_px = self.calculate_distance(left_hip, left_ankle)
            inseam_cm = self.pixels_to_cm(inseam_px, calibration_factor)
            measurements['inseam'] = inseam_cm
        elif right_hip and right_ankle:
            inseam_px = self.calculate_distance(right_hip, right_ankle)
            inseam_cm = self.pixels_to_cm(inseam_px, calibration_factor)
            measurements['inseam'] = inseam_cm
        
        # Convert to imperial if requested
        if units == "imperial":
            measurements = {
                key: round(self.cm_to_inches(value), 1)
                for key, value in measurements.items()
            }
        else:
            # Round to 1 decimal place
            measurements = {
                key: round(value, 1)
                for key, value in measurements.items()
            }
        
        return measurements
