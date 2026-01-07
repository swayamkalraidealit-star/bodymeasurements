"""Face detection and mapping service using MediaPipe."""
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import base64
import io
from typing import Optional, Tuple


class FaceMapper:
    """Detect and extract faces from images using MediaPipe."""
    
    def __init__(self):
        """Initialize MediaPipe face detection."""
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # Full range model
            min_detection_confidence=0.5
        )
    
    def extract_face(self, image_base64: str) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Extract face region from image.
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Tuple of (cropped_face_image, face_info) or None if no face found
        """
        # Decode image
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return None
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        
        # Detect faces
        results = self.face_detection.process(image_rgb)
        
        if not results.detections:
            return None
        
        # Get first detected face
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        
        # Convert relative to absolute coordinates
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)
        
        # Add padding
        padding = int(min(width, height) * 0.2)
        x = max(0, x - padding)
        y = max(0, y - padding)
        width = min(w - x, width + 2 * padding)
        height = min(h - y, height + 2 * padding)
        
        # Crop face
        face_crop = image_rgb[y:y+height, x:x+width]
        
        face_info = {
            "bbox": (x, y, width, height),
            "confidence": detection.score[0],
            "original_size": (w, h)
        }
        
        return face_crop, face_info
    
    def align_face(self, face_image: np.ndarray) -> np.ndarray:
        """
        Align face for better overlay (basic implementation).
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Aligned face image
        """
        # For now, just ensure square aspect ratio
        h, w = face_image.shape[:2]
        
        if h != w:
            size = max(h, w)
            # Create square canvas
            square = np.zeros((size, size, 3), dtype=np.uint8)
            square[:] = (255, 255, 255)  # White background
            
            # Center the face
            y_offset = (size - h) // 2
            x_offset = (size - w) // 2
            square[y_offset:y_offset+h, x_offset:x_offset+w] = face_image
            
            return square
        
        return face_image
    
    def create_circular_mask(self, size: Tuple[int, int]) -> np.ndarray:
        """
        Create circular alpha mask for face.
        
        Args:
            size: (width, height) of mask
            
        Returns:
            Alpha mask as numpy array
        """
        mask = np.zeros(size, dtype=np.uint8)
        center = (size[0] // 2, size[1] // 2)
        radius = min(center[0], center[1])
        cv2.circle(mask, center, radius, 255, -1)
        
        # Add smooth edges
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        
        return mask
    
    def match_skin_tone(self, face_image: np.ndarray) -> Tuple[int, int, int]:
        """
        Determine dominant skin tone from face image.
        
        Args:
            face_image: Face image in RGB
            
        Returns:
            RGB tuple of dominant skin tone
        """
        # Get center region of face (likely skin)
        h, w = face_image.shape[:2]
        center_region = face_image[
            h//4:3*h//4,
            w//4:3*w//4
        ]
        
        # Calculate average color
        avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        
        return tuple(avg_color.astype(int))


# Singleton instance
face_mapper = FaceMapper()
