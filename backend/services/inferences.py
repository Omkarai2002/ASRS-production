# backend/services/inferences.py

from backend.services.google_ocr import OCRClient
from backend.services.annotations_parser import AnnotationsParser
from backend.services.data_manager import get_record, upload_result
from backend.services.json_result import build_result
from backend.services.s3_operator import upload_images
from backend.services.detection import detect_vehicle
import os

ocr_client = OCRClient()
parser = AnnotationsParser()

def process_single_image(image_path):
    """
    Process a single image:
    - Run OCR
    - Parse unique IDs
    - Get records from DB
    - Detect vehicle
    - Build final result
    """
    annotations = ocr_client.get_annotations(image_path)
    unique_ids = parser.get_unique_ids(annotations)
    records = [get_record(unique_id[0]) for unique_id in unique_ids]
    detection = detect_vehicle(image_path, records)
    image_name = os.path.basename(image_path)
    return build_result(image_name, records, detection)

def get_inferences(report_dir, report_id):
    """
    Process all images in a report directory:
    - Upload images to S3
    - Run inferences on each image
    - Save results to database
    """
    for image_name in os.listdir(report_dir):
        if image_name.lower().endswith((".jpg", ".png")):
            image_path = os.path.join(report_dir, image_name)
            # Process single image
            result = process_single_image(image_path)
            # Upload to S3
            s3_key, s3_url = upload_images(image_path)
            # Save result in DB
            upload_result(result, report_id, s3_url)
