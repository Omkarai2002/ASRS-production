# backend/services/inferences.py

import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.services.google_ocr import OCRClient
from backend.services.annotations_parser import AnnotationsParser
from backend.services.json_result import build_result
from backend.services.s3_operator import upload_images
from backend.services.detection import detect_vehicle
from backend.models.inference import Inference
from backend.services.data_manager import upload_result, get_record
import logging

logger = logging.getLogger(__name__)

ocr_client = OCRClient()
parser = AnnotationsParser()

# Maximum number of concurrent USER uploads (not images)
# Each user's images are processed sequentially
MAX_CONCURRENT_USERS = 4


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


def process_user_report_sequentially(report_dir, report_id, user_id):
    """
    Process all images in a single report sequentially.
    This function runs for ONE user's upload.
    Multiple users' reports run in parallel, but within each user,
    images are processed one after another to maintain order.
    
    Args:
        report_dir: Path to the report directory
        report_id: ID of the report
        user_id: ID of the user who uploaded
    
    Returns:
        Tuple of (success, total_processed, total_results)
    """
    try:
        # Get list of image files
        image_files = []
        for image_name in os.listdir(report_dir):
            if not image_name.lower().endswith((".jpg", ".png", ".jpeg")):
                continue
            image_files.append(os.path.join(report_dir, image_name))
        
        if not image_files:
            logger.warning(f"No image files found in {report_dir} for user {user_id}")
            return (True, 0, 0)
        
        logger.info(f"User {user_id}: Starting sequential processing of {len(image_files)} images")
        
        total_results = 0
        failed_images = 0
        
        # Process images sequentially for this user
        for idx, image_path in enumerate(image_files, 1):
            try:
                image_name = os.path.basename(image_path)
                logger.info(f"User {user_id}: Processing image {idx}/{len(image_files)}: {image_name}")
                
                # 1. Process the image
                results = process_single_image(image_path)

                # 2. Upload to S3
                s3_key, s3_url = upload_images(image_path)

                # 3. Create Inference objects for each result and save in DB
                for result in results:
                    inference = Inference(
                        report_id=report_id,
                        user_id=user_id,
                        image_name=result.get("IMG_NAME", ""),
                        unique_id=result.get("UNIQUE_ID", ""),
                        quantity=result.get("QUANTITY", 1),
                        vin_no=result.get("VIN_NO", ""),
                        exclusion=result.get("EXCLUSION", ""),
                        s3_obj_url=s3_url
                    )
                    upload_result(inference)
                
                total_results += len(results)
                logger.info(f"User {user_id}: ✅ Image {idx}/{len(image_files)} complete ({len(results)} results)")
            
            except Exception as e:
                failed_images += 1
                logger.error(f"User {user_id}: ❌ Error processing image {image_name}: {str(e)}")
        
        success = failed_images == 0
        logger.info(f"User {user_id}: Completed {len(image_files) - failed_images}/{len(image_files)} images, {total_results} total results")
        return (success, len(image_files) - failed_images, total_results)
    
    except Exception as e:
        logger.error(f"User {user_id}: Critical error in process_user_report_sequentially: {str(e)}")
        return (False, 0, 0)


def get_inferences(report_dir, report_id, user_id=None):
    """
    Process reports for multiple users in parallel.
    
    Key Design:
    - Different users' reports process IN PARALLEL (up to MAX_CONCURRENT_USERS)
    - Within each user's report, images process SEQUENTIALLY
    - Maintains upload order per user
    - Maximizes parallelism across users
    
    Args:
        report_dir: Path to the report directory
        report_id: ID of the report
        user_id: ID of the user who uploaded
    """

    try:
        logger.info(f"Starting inference processing for Report {report_id}, User {user_id}")
        
        # For single user uploads, just process sequentially
        if user_id:
            success, images_processed, total_results = process_user_report_sequentially(
                report_dir, report_id, user_id
            )
            logger.info(f"Report {report_id}: Processing complete - {images_processed} images, {total_results} results")
            return
        
        # Note: The parallel execution happens at the FastAPI level
        # Multiple users calling /upload endpoint simultaneously will each get their own
        # BackgroundTask, and these tasks run in parallel via ThreadPoolExecutor at the app level
        logger.warning("get_inferences called without user_id")
    
    finally:
        # Clean up the uploaded folder after processing completes
        if os.path.exists(report_dir):
            try:
                shutil.rmtree(report_dir)
                logger.info(f"Cleaned up processed folder: {report_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up folder {report_dir}: {str(e)}")