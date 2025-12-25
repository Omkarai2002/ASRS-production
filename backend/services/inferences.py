# backend/services/inferences.py

import os
import shutil
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from backend.services.google_ocr import OCRClient
from backend.services.annotations_parser import AnnotationsParser
from backend.services.json_result import build_result
from backend.services.s3_operator import upload_images
from backend.services.detection import detect_vehicle
from backend.models.inference import Inference
from backend.services.data_manager import upload_result, get_record
import logging
from datetime import datetime

# Hard Requirement: Set start method to 'spawn' to avoid CUDA/Torch issues with fork
# force=True prevents errors if it was already set (e.g. by another module)
try:
    mp.set_start_method("spawn", force=True)
except RuntimeError:
    pass  # Context might be already set

logger = logging.getLogger(__name__)

ocr_client = OCRClient()
parser = AnnotationsParser()

# Global ProcessPoolExecutor REMOVED to ensure clean shutdown
# Pools will be created per-request using context managers

# Maximum number of concurrent USER uploads (not images)
# Each user's images are processed sequentially
MAX_CONCURRENT_USERS = 8


def process_single_image(image_path, process_pool):
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
    
    # Offload detection to the passed ProcessPoolExecutor
    # This prevents creating a new pool for every image
    future = process_pool.submit(detect_vehicle, image_path, unique_ids)
    detection = future.result()

    print("detections: ",detection)
    image_name = os.path.basename(image_path)

    return build_result(image_name, records, detection)


def process_single_image_pipeline(image_path, report_id, user_id, idx, total_files, process_pool):
    """
    Helper function to run the full pipeline for one image.
    Executed in a Thread (via ThreadPoolExecutor).
    """
    image_name = os.path.basename(image_path)
    try:
        logger.info(f"User {user_id}: Processing image {idx}/{total_files}: {image_name}")
        
        # 1. Process the image (OCR + Detection in ProcessPool)
        results = process_single_image(image_path, process_pool)

        # 2. Upload to S3
        s3_key, s3_url = upload_images(image_path)

        # 3. Create Inference objects for each result and save in DB
        saved_count = 0
        for result in results:
            inference = Inference(
                report_id=report_id,
                user_id=user_id,
                image_name=result.get("IMG_NAME", ""),
                unique_id=result.get("UNIQUE_ID", ""),
                quantity=result.get("QUANTITY", 1),
                vin_no=result.get("VIN_NO", ""),
                exclusion=result.get("EXCLUSION", ""),
                s3_obj_url=s3_url,
                createdAt=datetime.now()
            )
            upload_result(inference)
            saved_count += 1
        
        logger.info(f"User {user_id}: ✅ Image {idx}/{total_files} complete ({saved_count} results)")
        return (True, saved_count)

    except Exception as e:
        logger.error(f"User {user_id}: ❌ Error processing image {image_name}: {str(e)}")
        return (False, 0)


def process_user_report_concurrently(report_dir, report_id, user_id):
    """
    Process all images in a single report concurrently.
    Multiple threads handle different images.
    CPU-bound detection is offloaded to a ProcessPool.
    
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
        
        logger.info(f"User {user_id}: Starting CONCURRENT processing of {len(image_files)} images")
        
        total_results = 0
        failed_count = 0
        total_files = len(image_files)
        
        # Use ThreadPoolExecutor for I/O bound concurrency
        # We cap workers to avoid too many DB connections or rate limits
        max_threads = min(8, total_files)
        
        # Use Context Managers for strict cleanup!
        # This ensures pools are closed and processes joined.
        # spawn is required for CUDA/Torch compatibility.
        mp_context = mp.get_context('spawn')
        
        with ProcessPoolExecutor(max_workers=8, mp_context=mp_context) as process_pool:
            with ThreadPoolExecutor(max_workers=max_threads) as thread_pool:
                # Submit all tasks
                future_to_file = {
                    thread_pool.submit(process_single_image_pipeline, img_path, report_id, user_id, i, total_files, process_pool): img_path 
                    for i, img_path in enumerate(image_files, 1)
                }
                
                for future in as_completed(future_to_file):
                    success, count = future.result()
                    if success:
                        total_results += count
                    else:
                        failed_count += 1
        
        success_status = (failed_count == 0)
        logger.info(f"User {user_id}: Completed {total_files - failed_count}/{total_files} images, {total_results} total results")
        return (success_status, total_files - failed_count, total_results)
    
    except Exception as e:
        logger.error(f"User {user_id}: Critical error in process_user_report_concurrently: {str(e)}")
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
    print("multiprocessing enabled")
    try:
        logger.info(f"Starting inference processing for Report {report_id}, User {user_id}")
        
        # For single user uploads, just process sequentially
        if user_id:
            success, images_processed, total_results = process_user_report_concurrently(
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


