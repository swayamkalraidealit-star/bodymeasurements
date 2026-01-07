"""Clothing overlay service for virtual try-on."""
import cv2
import numpy as np
from PIL import Image
import base64
import io
import os
from typing import Tuple, Optional

from app.core.config import settings


class ClothingOverlay:
    """Overlay clothing on avatar images."""
    
    def __init__(self):
        """Initialize clothing overlay service."""
        self.clothing_dir = settings.clothing_assets_dir
    
    def overlay_garment(
        self,
        avatar_image_base64: str,
        garment_id: str,
        scale_factor: float = 1.0
    ) -> str:
        """
        Overlay a garment onto an avatar.
        
        Args:
            avatar_image_base64: Base64 encoded avatar image
            garment_id: ID of garment to overlay
            scale_factor: Scaling factor for garment
            
        Returns:
            Base64 encoded image with garment overlay
        """
        # Decode avatar image
        avatar_data = base64.b64decode(avatar_image_base64)
        avatar_img = Image.open(io.BytesIO(avatar_data)).convert('RGBA')
        avatar_array = np.array(avatar_img)
        
        # For now, create a simple placeholder garment overlay
        # In production, this would load actual garment assets
        garment_overlay = self._create_placeholder_garment(
            avatar_array.shape,
            garment_id
        )
        
        # Composite garment onto avatar
        result = self._composite_images(avatar_array, garment_overlay)
        
        # Convert back to base64
        result_img = Image.fromarray(result)
        buffered = io.BytesIO()
        result_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def _create_placeholder_garment(
        self,
        shape: Tuple[int, int, int],
        garment_id: str
    ) -> np.ndarray:
        """
        Create a placeholder garment overlay.
        
        This is a simplified version. In production, you would:
        1. Load actual garment image from assets
        2. Scale and position based on avatar landmarks
        3. Apply warping for natural fit
        """
        h, w = shape[:2]
        garment = np.zeros((h, w, 4), dtype=np.uint8)
        
        # Determine garment type and color
        if "shirt" in garment_id or "tshirt" in garment_id:
            # Draw a simple shirt overlay
            color = (70, 130, 180, 200)  # Steel blue with transparency
            
            # Torso area (simplified)
            cv2.rectangle(
                garment,
                (int(w * 0.25), int(h * 0.25)),
                (int(w * 0.75), int(h * 0.55)),
                color,
                -1
            )
            
            # Add some detail (collar)
            cv2.rectangle(
                garment,
                (int(w * 0.4), int(h * 0.25)),
                (int(w * 0.6), int(h * 0.28)),
                (50, 50, 50, 200),
                -1
            )
            
        elif "jeans" in garment_id or "pants" in garment_id:
            # Draw simple pants
            color = (30, 60, 110, 200)  # Denim blue
            
            # Left leg
            cv2.rectangle(
                garment,
                (int(w * 0.3), int(h * 0.55)),
                (int(w * 0.45), int(h * 0.9)),
                color,
                -1
            )
            
            # Right leg
            cv2.rectangle(
                garment,
                (int(w * 0.55), int(h * 0.55)),
                (int(w * 0.7), int(h * 0.9)),
                color,
                -1
            )
        
        return garment
    
    def _composite_images(
        self,
        background: np.ndarray,
        overlay: np.ndarray
    ) -> np.ndarray:
        """
        Composite overlay onto background using alpha blending.
        
        Args:
            background: Background image (avatar)
            overlay: Overlay image (garment)
            
        Returns:
            Composited image
        """
        # Ensure both images have alpha channel
        if background.shape[2] == 3:
            background = cv2.cvtColor(background, cv2.COLOR_RGB2RGBA)
        if overlay.shape[2] == 3:
            overlay = cv2.cvtColor(overlay, cv2.COLOR_RGB2RGBA)
        
        # Alpha blending
        alpha_overlay = overlay[:, :, 3] / 255.0
        alpha_background = 1.0 - alpha_overlay
        
        for c in range(3):
            background[:, :, c] = (
                alpha_overlay * overlay[:, :, c] +
                alpha_background * background[:, :, c]
            )
        
        return background


# Singleton instance
clothing_overlay = ClothingOverlay()
