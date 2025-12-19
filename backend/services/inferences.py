# backend/services/inferences.py

import os
import shutil
from backend.services.google_ocr import OCRClient
from backend.services.annotations_parser import AnnotationsParser
from backend.services.json_result import build_result
from backend.services.s3_operator import upload_images
from backend.services.detection import detect_vehicle
from backend.models.inference import Inference
from backend.services.data_manager import upload_result, get_record

ocr_client = OCRClient()
parser = AnnotationsParser()


def process_single_image(image_path):
    """
    Process a single image:
    - Run OCR
    - Parse Unique IDs
    - Detect vehicle
    - Build final result JSON
    """
    annotations = ocr_client.get_annotations(image_path)
    unique_ids = parser.get_unique_ids(annotations)
    records = [get_record(unique_id[0]) for unique_id in unique_ids]  # NEW LINE
    # No DB lookup anymore (get_record deleted)
    detection = detect_vehicle(image_path, unique_ids)
    print("detections: ",detection)
    image_name = os.path.basename(image_path)

    return build_result(image_name, records, detection)


def get_inferences(report_dir, report_id, user_id=None):
    """
    Process all images:
    - Run OCR + detection
    - Upload to S3
    - Save each result row in DB
    - Clean up uploaded folder after processing
    """

    try:
        for image_name in os.listdir(report_dir):
            if not image_name.lower().endswith((".jpg", ".png", ".jpeg")):
                continue

            image_path = os.path.join(report_dir, image_name)

            # 1. Process the image
            results = process_single_image(image_path)  # Returns a LIST of dicts

            # results is a list from build_result() like:
            # [
            #   {
            #     "IMG_NAME": "",
            #     "UNIQUE_ID": "",
            #     "QUANTITY": "",
            #     "VIN_NO": "",
            #     "EXCLUSION": ""
            #   },
            #   ...
            # ]

            # 2. Upload to S3
            s3_key, s3_url = upload_images(image_path)

            # 3. Create Inference objects for each result and save in DB
            for result in results:
                inference = Inference(
                    report_id=report_id,
                    user_id=user_id,  # NEW: Store user_id with inference
                    image_name=result.get("IMG_NAME", ""),
                    unique_id=result.get("UNIQUE_ID", ""),
                    quantity=result.get("QUANTITY", 1),
                    vin_no=result.get("VIN_NO", ""),
                    exclusion=result.get("EXCLUSION", ""),
                    s3_obj_url=s3_url
                )
                
                upload_result(inference)
    finally:
        # Clean up the uploaded folder after processing completes
        if os.path.exists(report_dir):
            try:
                shutil.rmtree(report_dir)
                print(f"Cleaned up processed folder: {report_dir}")
            except Exception as e:
                print(f"Error cleaning up folder {report_dir}: {str(e)}")

