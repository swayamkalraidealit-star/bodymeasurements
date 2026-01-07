"""API routes for body measurements."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    MeasurementRequest,
    MeasurementResponse,
    Measurements,
    LandmarkData,
    HealthResponse,
    ErrorResponse
)
from app.services.pose_detector import PoseDetector
from app.services.measurement_calculator import MeasurementCalculator
from app.utils.image_processor import ImageProcessor
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.core.database import get_measurements_collection
from app.models.models import User, UserMeasurementDB
from fastapi import Depends
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services (singleton)
pose_detector = PoseDetector()
measurement_calculator = MeasurementCalculator()
image_processor = ImageProcessor()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


@router.post("/calculate", response_model=MeasurementResponse)
async def calculate_measurements(
    request: MeasurementRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate body measurements from uploaded images.
    
    Args:
        request: MeasurementRequest containing images and calibration data
        
    Returns:
        MeasurementResponse with calculated measurements
    """
    try:
        logger.info("Processing measurement request")
        
        # Process front image
        logger.info("Decoding front image")
        front_image = image_processor.base64_to_image(request.front_image)
        
        # Validate front image
        is_valid, error_msg = image_processor.validate_image(front_image)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Front image validation failed: {error_msg}")
        
        # Resize if needed
        front_image = image_processor.resize_image(front_image)
        
        # Prepare for MediaPipe
        front_rgb = image_processor.prepare_for_mediapipe(front_image)
        
        # Detect pose landmarks
        logger.info("Detecting pose landmarks in front image")
        front_landmarks = pose_detector.detect_landmarks(front_rgb)
        
        if not front_landmarks:
            return MeasurementResponse(
                success=False,
                measurements=None,
                landmarks_detected=False,
                confidence_score=None,
                message="Could not detect pose in front image. Please ensure full body is visible with good lighting."
            )
        
        # Process side image if provided
        side_landmarks = None
        if request.side_image:
            logger.info("Processing side image")
            try:
                side_image = image_processor.base64_to_image(request.side_image)
                is_valid, error_msg = image_processor.validate_image(side_image)
                
                if is_valid:
                    side_image = image_processor.resize_image(side_image)
                    side_rgb = image_processor.prepare_for_mediapipe(side_image)
                    side_landmarks = pose_detector.detect_landmarks(side_rgb)
                    
                    if side_landmarks:
                        logger.info(f"Side pose detected with confidence: {side_landmarks['confidence']:.2f}")
                    else:
                        logger.warning("Could not detect pose in side image, proceeding with front only")
                else:
                    logger.warning(f"Side image validation failed: {error_msg}")
            except Exception as e:
                logger.warning(f"Error processing side image: {str(e)}, proceeding with front only")
        
        # Calculate measurements
        logger.info("Calculating measurements")
        measurements_dict = measurement_calculator.calculate_measurements(
            front_landmarks=front_landmarks,
            side_landmarks=side_landmarks,
            calibration_height_cm=request.calibration_height,
            units=request.units,
            gender=request.gender
        )
        
        if not measurements_dict:
            return MeasurementResponse(
                success=False,
                measurements=None,
                landmarks_detected=True,
                confidence_score=front_landmarks['confidence'],
                message="Landmarks detected but unable to calculate measurements. Please try a different pose."
            )
        
        # Create measurements object
        measurements = Measurements(
            shoulder_width=measurements_dict.get('shoulder_width'),
            chest=measurements_dict.get('chest'),
            waist=measurements_dict.get('waist'),
            hip=measurements_dict.get('hip'),
            height=measurements_dict.get('height'),
            inseam=measurements_dict.get('inseam'),
            units="inches" if request.units == "imperial" else "cm"
        )
        
        # Convert landmarks to response format
        front_landmark_data = [
            LandmarkData(
                x=lm['x'],
                y=lm['y'],
                z=lm['z'],
                visibility=lm['visibility']
            )
            for lm in front_landmarks['landmarks']
        ]
        
        side_landmark_data = None
        if side_landmarks:
            side_landmark_data = [
                LandmarkData(
                    x=lm['x'],
                    y=lm['y'],
                    z=lm['z'],
                    visibility=lm['visibility']
                )
                for lm in side_landmarks['landmarks']
            ]
        
        logger.info(f"Successfully calculated {len(measurements_dict)} measurements")
        
        # Save to database
        try:
            measurements_collection = get_measurements_collection()
            measurement_db = UserMeasurementDB(
                user_id=current_user.id,
                measurements=measurements_dict,
                gender=request.gender,
                height=request.calibration_height,
                units=request.units
            )
            await measurements_collection.insert_one(measurement_db.model_dump(by_alias=True))
            logger.info(f"Saved measurements for user {current_user.id}")
        except Exception as e:
            logger.error(f"Error saving measurements to database: {str(e)}")
            # Don't fail the request if saving fails, but log it
        
        return MeasurementResponse(
            success=True,
            measurements=measurements,
            landmarks_detected=True,
            confidence_score=front_landmarks['confidence'],
            message=f"Successfully calculated {len(measurements_dict)} measurements",
            front_landmarks=front_landmark_data,
            side_landmarks=side_landmark_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating measurements: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/history")
async def get_measurement_history(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get measurement history for the current user.
    """
    try:
        measurements_collection = get_measurements_collection()
        cursor = measurements_collection.find({"user_id": current_user.id}).sort("created_at", -1)
        history = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            history.append(doc)
        return {"success": True, "history": history}
    except Exception as e:
        logger.error(f"Error fetching measurement history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
