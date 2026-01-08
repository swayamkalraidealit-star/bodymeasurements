import cv2
import numpy as np
import os
import sys

# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

from app.services.pose_detector import PoseDetector
from app.services.measurement_calculator import MeasurementCalculator

def run_test():
    detector = PoseDetector()
    calculator = MeasurementCalculator()
    
    # Paths to the provided images
    front_image_path = "/home/ideal39/.gemini/antigravity/brain/e6286c43-2208-4ffa-97f7-d6518190177b/uploaded_image_1_1767783546688.png"
    side_image_path = "/home/ideal39/.gemini/antigravity/brain/e6286c43-2208-4ffa-97f7-d6518190177b/uploaded_image_0_1767783546688.png"
    
    print(f"Loading front image: {front_image_path}")
    front_img = cv2.imread(front_image_path)
    if front_img is None:
        print("Error: Could not load front image")
        return
    
    front_results = detector.detect_landmarks(front_img)
    if not front_results['landmarks']:
        print("Error: No landmarks detected in front image")
        return
    
    print(f"Front landmarks detected with confidence: {front_results['confidence']:.2f}")
    
    print(f"Loading side image: {side_image_path}")
    side_img = cv2.imread(side_image_path)
    side_results = None
    if side_img is not None:
        side_results = detector.detect_landmarks(side_img)
        if side_results['landmarks']:
            print(f"Side landmarks detected with confidence: {side_results['confidence']:.2f}")
        else:
            print("Warning: No landmarks detected in side image")
            side_results = None
    
    # Test parameters
    height_cm = 170.0
    gender = "female"
    
    print(f"\nCalculating measurements (Height: {height_cm}cm, Gender: {gender})...")
    measurements = calculator.calculate_measurements(
        front_results,
        side_results,
        height_cm,
        gender=gender
    )
    
    print("\nResults:")
    for key, value in measurements.items():
        print(f"  {key}: {value} cm")

if __name__ == "__main__":
    run_test()
