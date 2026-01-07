"""2D Avatar generator from body measurements."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from typing import Dict, Tuple, Optional
import base64
import io
from datetime import datetime
import os
import uuid

from app.core.config import settings
from app.models.schemas import Measurements
from app.models.garment_data import SkinTone


class AvatarGenerator:
    """Generate 2D avatars from body measurements using component-based approach."""
    
    # Skin tone RGB values
    SKIN_TONES = {
        SkinTone.LIGHT: (255, 224, 189),
        SkinTone.MEDIUM_LIGHT: (241, 194, 125),
        SkinTone.MEDIUM: (224, 172, 105),
        SkinTone.MEDIUM_DARK: (198, 134, 66),
        SkinTone.DARK: (141, 85, 36),
    }
    
    def __init__(self):
        """Initialize avatar generator."""
        self.avatar_width = settings.avatar_image_width
        self.avatar_height = settings.avatar_image_height
        self.storage_dir = settings.avatar_storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def generate_avatar(
        self,
        measurements: Measurements,
        skin_tone: SkinTone = SkinTone.MEDIUM,
        gender: str = "neutral"
    ) -> Dict[str, str]:
        """
        Generate a 2D avatar from body measurements.
        
        Args:
            measurements: User's body measurements
            skin_tone: Skin tone selection
            gender: Gender (male, female, neutral)
            
        Returns:
            Dict with avatar_id, image_data (base64), and file_path
        """
        # Create canvas
        avatar_image = Image.new('RGBA', (self.avatar_width, self.avatar_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(avatar_image)
        
        # Get skin tone color
        skin_color = self.SKIN_TONES.get(skin_tone, self.SKIN_TONES[SkinTone.MEDIUM])
        
        # Calculate proportions from measurements
        proportions = self._calculate_proportions(measurements)
        
        # Draw avatar components
        self._draw_body(draw, proportions, skin_color, gender)
        
        # Generate unique ID
        avatar_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to file
        filename = f"avatar_{avatar_id}_{timestamp}.png"
        file_path = os.path.join(self.storage_dir, filename)
        avatar_image.save(file_path, "PNG")
        
        # Convert to base64
        buffered = io.BytesIO()
        avatar_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "avatar_id": avatar_id,
            "image_data": img_base64,
            "file_path": file_path,
            "timestamp": timestamp
        }
    
    def _calculate_proportions(self, measurements: Measurements) -> Dict[str, float]:
        """
        Calculate avatar proportions from measurements.
        
        Uses human body proportions (head = 1/8 of height, etc.)
        """
        height_cm = measurements.height or 170.0
        shoulder_width_cm = measurements.shoulder_width or 45.0
        chest_cm = measurements.chest or 95.0
        waist_cm = measurements.waist or 80.0
        hip_cm = measurements.hip or 95.0
        
        # Convert to pixels (scaling to fit canvas)
        height_px = self.avatar_height * 0.9  # Leave 10% margin
        scale_factor = height_px / height_cm
        
        # Standard proportions
        head_height = height_px / 8
        torso_height = height_px * 0.35
        leg_height = height_px * 0.45
        
        # Widths (converted to pixels)
        shoulder_width_px = shoulder_width_cm * scale_factor
        chest_width_px = (chest_cm / np.pi) * scale_factor  # Approx width from circumference
        waist_width_px = (waist_cm / np.pi) * scale_factor
        hip_width_px = (hip_cm / np.pi) * scale_factor
        
        return {
            "height": height_px,
            "head_height": head_height,
            "torso_height": torso_height,
            "leg_height": leg_height,
            "shoulder_width": shoulder_width_px,
            "chest_width": chest_width_px,
            "waist_width": waist_width_px,
            "hip_width": hip_width_px,
            "scale_factor": scale_factor,
            "center_x": self.avatar_width / 2
        }
    
    def _draw_body(
        self,
        draw: ImageDraw.ImageDraw,
        proportions: Dict[str, float],
        skin_color: Tuple[int, int, int],
        gender: str
    ):
        """Draw the avatar body parts."""
        cx = proportions["center_x"]
        
        # Starting Y positions
        head_y = 50
        neck_y = head_y + proportions["head_height"]
        torso_y = neck_y + 20
        hip_y = torso_y + proportions["torso_height"]
        leg_bottom_y = hip_y + proportions["leg_height"]
        
        # Draw head (circle)
        head_radius = proportions["head_height"] / 2
        head_bbox = [
            cx - head_radius,
            head_y,
            cx + head_radius,
            head_y + proportions["head_height"]
        ]
        draw.ellipse(head_bbox, fill=skin_color, outline=(100, 100, 100), width=2)
        
        # Draw neck
        neck_width = 30
        draw.rectangle(
            [cx - neck_width/2, neck_y, cx + neck_width/2, torso_y],
            fill=skin_color,
            outline=(100, 100, 100),
            width=1
        )
        
        # Draw torso (trapezoid: shoulders wider at top, narrows to waist)
        shoulder_half = proportions["shoulder_width"] / 2
        waist_half = proportions["waist_width"] / 2
        
        torso_points = [
            (cx - shoulder_half, torso_y),  # Left shoulder
            (cx + shoulder_half, torso_y),  # Right shoulder
            (cx + waist_half, hip_y - 40),  # Right waist
            (cx - waist_half, hip_y - 40),  # Left waist
        ]
        draw.polygon(torso_points, fill=skin_color, outline=(100, 100, 100))
        
        # Draw hips (rectangle)
        hip_half = proportions["hip_width"] / 2
        draw.rectangle(
            [cx - hip_half, hip_y - 40, cx + hip_half, hip_y],
            fill=skin_color,
            outline=(100, 100, 100),
            width=1
        )
        
        # Draw legs
        leg_width = 40
        # Left leg
        draw.rectangle(
            [cx - hip_half + 10, hip_y, cx - 10, leg_bottom_y],
            fill=skin_color,
            outline=(100, 100, 100),
            width=2
        )
        # Right leg
        draw.rectangle(
            [cx + 10, hip_y, cx + hip_half - 10, leg_bottom_y],
            fill=skin_color,
            outline=(100, 100, 100),
            width=2
        )
        
        # Draw arms
        arm_length = proportions["torso_height"] + 40
        arm_width = 25
        
        # Left arm
        draw.rectangle(
            [cx - shoulder_half - arm_width, torso_y, cx - shoulder_half, torso_y + arm_length],
            fill=skin_color,
            outline=(100, 100, 100),
            width=2
        )
        # Right arm
        draw.rectangle(
            [cx + shoulder_half, torso_y, cx + shoulder_half + arm_width, torso_y + arm_length],
            fill=skin_color,
            outline=(100, 100, 100),
            width=2
        )
        
        # Draw hands (ovals)
        hand_size = 20
        # Left hand
        draw.ellipse(
            [
                cx - shoulder_half - arm_width/2 - hand_size/2,
                torso_y + arm_length,
                cx - shoulder_half - arm_width/2 + hand_size/2,
                torso_y + arm_length + hand_size
            ],
            fill=skin_color,
            outline=(100, 100, 100),
            width=1
        )
        # Right hand
        draw.ellipse(
            [
                cx + shoulder_half + arm_width/2 - hand_size/2,
                torso_y + arm_length,
                cx + shoulder_half + arm_width/2 + hand_size/2,
                torso_y + arm_length + hand_size
            ],
            fill=skin_color,
            outline=(100, 100, 100),
            width=1
        )
        
        # Draw facial features (simple)
        self._draw_face(draw, cx, head_y + proportions["head_height"]/2, head_radius * 0.8)
    
    def _draw_face(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float):
        """Draw simple facial features."""
        # Eyes
        eye_y = cy - radius * 0.2
        eye_spacing = radius * 0.4
        eye_size = 8
        
        # Left eye
        draw.ellipse(
            [cx - eye_spacing - eye_size, eye_y - eye_size/2,
             cx - eye_spacing, eye_y + eye_size/2],
            fill=(50, 50, 50)
        )
        # Right eye
        draw.ellipse(
            [cx + eye_spacing, eye_y - eye_size/2,
             cx + eye_spacing + eye_size, eye_y + eye_size/2],
            fill=(50, 50, 50)
        )
        
        # Nose (simple line)
        nose_y = cy
        draw.line(
            [(cx, eye_y + 10), (cx, nose_y + 10)],
            fill=(100, 100, 100),
            width=2
        )
        
        # Mouth (smile arc)
        mouth_y = cy + radius * 0.3
        mouth_width = radius * 0.6
        draw.arc(
            [cx - mouth_width, mouth_y - 10, cx + mouth_width, mouth_y + 15],
            start=0,
            end=180,
            fill=(100, 100, 100),
            width=2
        )
    
    def add_face_overlay(
        self,
        avatar_path: str,
        face_image_base64: str
    ) -> str:
        """
        Overlay a user's face onto the avatar.
        
        Args:
            avatar_path: Path to avatar image
            face_image_base64: Base64 encoded face image
            
        Returns:
            Base64 encoded avatar with face
        """
        # Load avatar
        avatar = Image.open(avatar_path).convert('RGBA')
        
        # Decode face image
        face_data = base64.b64decode(face_image_base64)
        face_image = Image.open(io.BytesIO(face_data)).convert('RGBA')
        
        # TODO: Implement face detection and mapping
        # For now, just resize and place face at approximate head position
        head_size = int(self.avatar_height / 8)
        face_resized = face_image.resize((head_size * 2, head_size * 2), Image.Resampling.LANCZOS)
        
        # Create circular mask for face
        mask = Image.new('L', face_resized.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), face_resized.size], fill=255)
        
        # Composite face onto avatar
        face_position = (int(self.avatar_width / 2 - head_size), 50)
        avatar.paste(face_resized, face_position, mask)
        
        # Save updated avatar
        avatar.save(avatar_path, "PNG")
        
        # Return base64
        buffered = io.BytesIO()
        avatar.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()


# Singleton instance
avatar_generator = AvatarGenerator()
