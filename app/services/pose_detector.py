"""Pose detection service using MediaPipe."""
import mediapipe as mp
import numpy as np
from typing import Optional, List, Dict
from app.core.config import settings


class PoseDetector:
    """Singleton pose detector using MediaPipe."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of PoseDetector exists."""
        if cls._instance is None:
            cls._instance = super(PoseDetector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize MediaPipe Pose."""
        if self._initialized:
            return
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=settings.mediapipe_model_complexity,
            enable_segmentation=True,
            min_detection_confidence=settings.mediapipe_min_detection_confidence,
        )
        self._initialized = True
    
    def detect_landmarks(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect pose landmarks in an image.
        
        Args:
            image: RGB image (numpy array)
            
        Returns:
            Dictionary with landmarks and metadata, or None if detection failed
        """
        # Process image
        results = self.pose.process(image)
        
        if not results.pose_landmarks:
            return None
        
        # Extract landmarks
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        # Calculate average visibility/confidence
        avg_confidence = sum(lm['visibility'] for lm in landmarks) / len(landmarks)
        
        return {
            'landmarks': landmarks,
            'confidence': avg_confidence,
            'image_width': image.shape[1],
            'image_height': image.shape[0],
            'segmentation_mask': results.segmentation_mask if hasattr(results, 'segmentation_mask') else None
        }
    
    def get_landmark_coords(self, landmarks: List[Dict], index: int, image_width: int, image_height: int) -> Optional[tuple]:
        """
        Get pixel coordinates for a specific landmark.
        
        Args:
            landmarks: List of landmark dictionaries
            index: Landmark index (0-32)
            image_width: Image width in pixels
            image_height: Image height in pixels
            
        Returns:
            Tuple of (x, y) pixel coordinates, or None if landmark not visible
        """
        if index >= len(landmarks):
            return None
        
        landmark = landmarks[index]
        
        # Check visibility threshold
        if landmark['visibility'] < 0.5:
            return None
        
        # Convert normalized coordinates to pixels
        x = int(landmark['x'] * image_width)
        y = int(landmark['y'] * image_height)
        
        return (x, y)
    
    def close(self):
        """Release resources."""
        if hasattr(self, 'pose'):
            self.pose.close()


# MediaPipe Pose Landmark indices (for reference)
class PoseLandmark:
    """MediaPipe Pose landmark indices."""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32
