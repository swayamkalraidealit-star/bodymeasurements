"""Image processing utilities."""
import base64
import io
import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional


class ImageProcessor:
    """Handles image preprocessing and format conversions."""
    
    @staticmethod
    def base64_to_image(base64_string: str) -> np.ndarray:
        """
        Convert base64 string to OpenCV image (numpy array).
        
        Args:
            base64_string: Base64 encoded image string
            
        Returns:
            OpenCV image as numpy array (BGR format)
        """
        # Remove data URL prefix if present
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        
        # Convert to numpy array
        image_array = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_bgr
    
    @staticmethod
    def image_to_base64(image: np.ndarray) -> str:
        """
        Convert OpenCV image to base64 string.
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            Base64 encoded image string
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG")
        
        # Encode to base64
        base64_string = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{base64_string}"
    
    @staticmethod
    def validate_image(image: np.ndarray, min_resolution: Tuple[int, int] = (480, 640)) -> Tuple[bool, Optional[str]]:
        """
        Validate image quality and dimensions.
        
        Args:
            image: OpenCV image
            min_resolution: Minimum (height, width) required
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if image is None or image.size == 0:
            return False, "Invalid or empty image"
        
        height, width = image.shape[:2]
        
        if height < min_resolution[0] or width < min_resolution[1]:
            return False, f"Image resolution too low. Minimum: {min_resolution[1]}x{min_resolution[0]}"
        
        # Check aspect ratio (should be roughly portrait or square for body photos)
        aspect_ratio = width / height
        if aspect_ratio > 2.0 or aspect_ratio < 0.3:
            return False, "Invalid aspect ratio. Please use a full-body photo in portrait or landscape orientation"
        
        return True, None
    
    @staticmethod
    def resize_image(image: np.ndarray, max_dimension: int = 1280) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: OpenCV image
            max_dimension: Maximum width or height
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if height <= max_dimension and width <= max_dimension:
            return image
        
        # Calculate new dimensions
        if height > width:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        else:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        
        # Resize
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return resized
    
    @staticmethod
    def prepare_for_mediapipe(image: np.ndarray) -> np.ndarray:
        """
        Prepare image for MediaPipe processing.
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            RGB image ready for MediaPipe
        """
        # Convert BGR to RGB (MediaPipe expects RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return rgb_image
