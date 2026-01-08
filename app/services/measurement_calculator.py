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
        actual_height_cm: float,
        segmentation_mask: Optional[np.ndarray] = None
    ) -> Optional[float]:
        """
        Calculate pixels-per-cm calibration factor using known height.
        """
        # Get ankle landmarks
        left_ankle = self._get_landmark_point(landmarks, PoseLandmark.LEFT_ANKLE, 1, image_height)
        right_ankle = self._get_landmark_point(landmarks, PoseLandmark.RIGHT_ANKLE, 1, image_height)
        
        if not (left_ankle or right_ankle):
            return None
        
        # Use available ankle (prefer average if both present)
        if left_ankle and right_ankle:
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
        elif left_ankle:
            ankle_y = left_ankle[1]
        else:
            ankle_y = right_ankle[1]
        
        # Find top of head
        top_y = None
        if segmentation_mask is not None:
            # Find the highest pixel in the mask
            mask_indices = np.where(segmentation_mask > 0.5)
            if len(mask_indices[0]) > 0:
                top_y = np.min(mask_indices[0])
        
        # Fallback to nose if mask is unavailable or failed
        if top_y is None:
            nose = self._get_landmark_point(landmarks, PoseLandmark.NOSE, 1, image_height)
            if nose:
                # Nose is roughly 10-12% down from top of head
                # So we estimate top of head
                top_y = nose[1] - (abs(ankle_y - nose[1]) * 0.12)
            else:
                return None
        
        # Calculate height in pixels
        height_pixels = abs(ankle_y - top_y)
        
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
        
        if landmark['visibility'] < 0.65:
            return None
        
        x = landmark['x'] * image_width
        y = landmark['y'] * image_height
        
        return (x, y)

    def _get_body_dimension_at_y(
        self,
        segmentation_mask: np.ndarray,
        y_px: int,
        image_width: int,
        center_x: Optional[float] = None,
        min_x: Optional[float] = None,
        max_x: Optional[float] = None
    ) -> float:
        """
        Calculate the width/depth of the body silhouette at a specific Y-coordinate.
        
        Args:
            segmentation_mask: MediaPipe segmentation mask
            y_px: Y-coordinate in pixels
            image_width: Image width in pixels
            center_x: Optional center X to search around
            min_x: Optional minimum X to consider
            max_x: Optional maximum X to consider
            
        Returns:
            Dimension in pixels
        """
        if segmentation_mask is None or y_px < 0 or y_px >= segmentation_mask.shape[0]:
            return 0
        
        # Get the mask row at y
        row = segmentation_mask[int(y_px), :]
        
        # Apply X constraints if provided
        if min_x is not None or max_x is not None:
            constrained_row = np.zeros_like(row)
            start = int(max(0, min_x if min_x is not None else 0))
            end = int(min(image_width, max_x if max_x is not None else image_width))
            constrained_row[start:end] = row[start:end]
            row = constrained_row
        
        # Find pixels where mask > 0.7 (higher threshold for better accuracy)
        body_pixels = np.where(row > 0.7)[0]
        
        if len(body_pixels) < 2:
            return 0
        
        if center_x is not None:
            # Find all continuous segments
            diff = np.diff(body_pixels)
            breaks = np.where(diff > 5)[0] # 5 pixel gap is a break
            segments = np.split(body_pixels, breaks + 1)
            
            # Find segment containing center_x
            for seg in segments:
                if seg[0] <= center_x <= seg[-1]:
                    return float(seg[-1] - seg[0])
            
            # If no segment contains center_x, take the one closest to it
            closest_seg = min(segments, key=lambda s: min(abs(s - center_x)))
            return float(closest_seg[-1] - closest_seg[0])

        # Fallback to simple distance if no center_x
        return float(body_pixels[-1] - body_pixels[0])

    def _calculate_circumference(self, width: float, depth: float) -> float:
        """
        Calculate circumference using Ramanujan's approximation for an ellipse.
        
        Args:
            width: Body width in cm
            depth: Body depth in cm
            
        Returns:
            Circumference in cm
        """
        if width <= 0 or depth <= 0:
            return 0
            
        a = width / 2
        b = depth / 2
        
        # Ramanujan's approximation
        h = ((a - b) ** 2) / ((a + b) ** 2)
        circumference = math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
        
        return circumference
    
    def calculate_measurements(
        self,
        front_landmarks: Dict,
        side_landmarks: Optional[Dict],
        calibration_height_cm: float,
        units: str = "metric",
        gender: str = "male"
    ) -> Dict:
        """
        Calculate all body measurements using segmentation and ellipse approximation.
        """
        measurements = {}
        
        # Get calibration factor from front view using segmentation mask for top of head
        calibration_factor = self.calculate_calibration_factor(
            front_landmarks['landmarks'],
            front_landmarks['image_height'],
            calibration_height_cm,
            segmentation_mask=front_landmarks.get('segmentation_mask')
        )
        
        if not calibration_factor:
            return measurements
        
        # Front view data
        f_lms = front_landmarks['landmarks']
        f_mask = front_landmarks.get('segmentation_mask')
        f_w = front_landmarks['image_width']
        f_h = front_landmarks['image_height']
        
        # Side view data
        s_lms = side_landmarks['landmarks'] if side_landmarks else None
        s_mask = side_landmarks.get('segmentation_mask') if side_landmarks else None
        s_w = side_landmarks['image_width'] if side_landmarks else 0
        s_h = side_landmarks['image_height'] if side_landmarks else 0
        
        # Get key landmarks (front)
        l_shoulder = self._get_landmark_point(f_lms, PoseLandmark.LEFT_SHOULDER, f_w, f_h)
        r_shoulder = self._get_landmark_point(f_lms, PoseLandmark.RIGHT_SHOULDER, f_w, f_h)
        l_hip = self._get_landmark_point(f_lms, PoseLandmark.LEFT_HIP, f_w, f_h)
        r_hip = self._get_landmark_point(f_lms, PoseLandmark.RIGHT_HIP, f_w, f_h)
        nose = self._get_landmark_point(f_lms, PoseLandmark.NOSE, f_w, f_h)
        l_ankle = self._get_landmark_point(f_lms, PoseLandmark.LEFT_ANKLE, f_w, f_h)
        r_ankle = self._get_landmark_point(f_lms, PoseLandmark.RIGHT_ANKLE, f_w, f_h)
        
        if not (l_shoulder and r_shoulder and l_hip and r_hip):
            return measurements

        # 1. Shoulder Width (skeletal distance is usually accurate even with clothes)
        shoulder_width_px = self.calculate_distance(l_shoulder, r_shoulder)
        measurements['shoulder_width'] = self.pixels_to_cm(shoulder_width_px, calibration_factor)
        
        # 2. Height (use the same logic as calibration for consistency)
        ankle_y = (l_ankle[1] + r_ankle[1]) / 2 if (l_ankle and r_ankle) else (l_ankle[1] if l_ankle else r_ankle[1] if r_ankle else f_h)
        top_y = None
        if f_mask is not None:
            mask_indices = np.where(f_mask > 0.5)
            if len(mask_indices[0]) > 0:
                top_y = np.min(mask_indices[0])
        
        if top_y is None:
            top_y = nose[1] - (abs(ankle_y - nose[1]) * 0.12) if nose else 0
            
        height_px = abs(ankle_y - top_y)
        measurements['height'] = self.pixels_to_cm(height_px, calibration_factor)

        # Define vertical levels (Y-coordinates)
        shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2
        hip_y = (l_hip[1] + r_hip[1]) / 2
        torso_height = hip_y - shoulder_y
        
        # Chest level: ~25% down from shoulders to hips
        chest_y = shoulder_y + torso_height * 0.25
        # Waist level: ~60% down from shoulders to hips (usually the narrowest)
        waist_y = shoulder_y + torso_height * 0.60
        # Hip level: at the hip landmarks
        hip_y_level = hip_y
        
        levels = {
            'chest': chest_y,
            'waist': waist_y,
            'hip': hip_y_level
        }
        
        # Default depth-to-width ratios if side view is missing
        default_depth_ratios = {
            'chest': 0.7 if gender == 'male' else 0.65,
            'waist': 0.75 if gender == 'male' else 0.7,
            'hip': 0.8 if gender == 'male' else 0.75
        }
        
        # Clothing allowance factors (ease subtraction)
        # We subtract a bit more for depth as clothes/hair often inflate it more
        width_correction = 0.95 # 5% ease subtraction
        depth_correction = 0.92 # 8% ease subtraction
        
        # Calculate center X and torso bounds for front view
        f_center_x = (l_shoulder[0] + r_shoulder[0]) / 2
        f_torso_width_px = abs(l_shoulder[0] - r_shoulder[0])

        # Calculate center X and torso bounds for side view
        s_center_x = 0
        if side_landmarks:
            s_l_shoulder = self._get_landmark_point(s_lms, PoseLandmark.LEFT_SHOULDER, s_w, s_h)
            s_r_shoulder = self._get_landmark_point(s_lms, PoseLandmark.RIGHT_SHOULDER, s_w, s_h)
            s_l_hip = self._get_landmark_point(s_lms, PoseLandmark.LEFT_HIP, s_w, s_h)
            s_r_hip = self._get_landmark_point(s_lms, PoseLandmark.RIGHT_HIP, s_w, s_h)
            
            points = [p for p in [s_l_shoulder, s_r_shoulder, s_l_hip, s_r_hip] if p]
            if points:
                s_center_x = sum(p[0] for p in points) / len(points)

        for name, y_px in levels.items():
            # Define specific constraints for each level
            if name == 'chest':
                min_x_level = f_center_x - f_torso_width_px * 0.55
                max_x_level = f_center_x + f_torso_width_px * 0.55
            elif name == 'waist':
                min_x_level = f_center_x - f_torso_width_px * 0.5
                max_x_level = f_center_x + f_torso_width_px * 0.5
            else: # hip
                min_x_level = f_center_x - f_torso_width_px * 0.65
                max_x_level = f_center_x + f_torso_width_px * 0.65

            # Get width from front view
            width_px = self._get_body_dimension_at_y(f_mask, y_px, f_w, center_x=f_center_x, min_x=min_x_level, max_x=max_x_level)
            width_cm = self.pixels_to_cm(width_px, calibration_factor) * width_correction
            
            # Get depth from side view if available
            depth_cm = 0
            if side_landmarks and s_mask is not None:
                s_calibration_factor = self.calculate_calibration_factor(s_lms, s_h, calibration_height_cm, segmentation_mask=s_mask)
                if s_calibration_factor:
                    # Find landmarks in side view to align Y
                    s_l_shoulder = self._get_landmark_point(s_lms, PoseLandmark.LEFT_SHOULDER, s_w, s_h)
                    s_r_shoulder = self._get_landmark_point(s_lms, PoseLandmark.RIGHT_SHOULDER, s_w, s_h)
                    s_shoulder_y = (s_l_shoulder[1] + s_r_shoulder[1]) / 2 if (s_l_shoulder and s_r_shoulder) else (s_l_shoulder[1] if s_l_shoulder else s_r_shoulder[1] if s_r_shoulder else 0)
                    
                    s_l_hip = self._get_landmark_point(s_lms, PoseLandmark.LEFT_HIP, s_w, s_h)
                    s_r_hip = self._get_landmark_point(s_lms, PoseLandmark.RIGHT_HIP, s_w, s_h)
                    s_hip_y = (s_l_hip[1] + s_r_hip[1]) / 2 if (s_l_hip and s_r_hip) else (s_l_hip[1] if s_l_hip else s_r_hip[1] if s_r_hip else 0)
                    
                    s_torso_height = s_hip_y - s_shoulder_y
                    
                    if name == 'chest':
                        s_y = s_shoulder_y + s_torso_height * 0.25
                    elif name == 'waist':
                        s_y = s_shoulder_y + s_torso_height * 0.60
                    else: # hip
                        s_y = s_hip_y
                        
                    # Side depth constraint: usually not more than 70% of shoulder width for slim people
                    s_max_depth_px = f_torso_width_px * 0.7 * (s_calibration_factor / calibration_factor)
                    s_min_x_level = s_center_x - s_max_depth_px / 2
                    s_max_x_level = s_center_x + s_max_depth_px / 2
                    
                    depth_px = self._get_body_dimension_at_y(s_mask, s_y, s_w, center_x=s_center_x, min_x=s_min_x_level, max_x=s_max_x_level)
                    depth_cm = self.pixels_to_cm(depth_px, s_calibration_factor) * depth_correction
            
            # Fallback for depth
            if depth_cm <= 0:
                depth_cm = width_cm * default_depth_ratios[name]
            
            # Calculate circumference
            circ = self._calculate_circumference(width_cm, depth_cm)
            
            # Sanity check: circumference should be within realistic bounds
            if circ > 140:
                circ = width_cm * 2.3
                
            measurements[name] = circ
            
        # 6. Inseam (crotch to ankle)
        crotch_y = hip_y + (torso_height * 0.18)
        ankle_y_val = (l_ankle[1] + r_ankle[1]) / 2 if (l_ankle and r_ankle) else (l_ankle[1] if l_ankle else r_ankle[1] if r_ankle else f_h)
        inseam_px = abs(ankle_y_val - crotch_y)
        measurements['inseam'] = self.pixels_to_cm(inseam_px, calibration_factor)
        
        # Convert to imperial if requested
        if units == "imperial":
            measurements = {
                key: round(self.cm_to_inches(value), 1)
                for key, value in measurements.items()
            }
        else:
            measurements = {
                key: round(value, 1)
                for key, value in measurements.items()
            }
        
        return measurements
