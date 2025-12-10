# backend/services/detection.py
import cv2

def detect_vehicle(image_path, records):
    """
    Dummy detection logic — replace with actual YOLO detection.
    """
    image = cv2.imread(image_path)

    if image is None:
        return False

    # Example simple detection logic:
    if records:
        return True
    return False
