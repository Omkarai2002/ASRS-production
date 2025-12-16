from backend.services.google_ocr import OCRClient
from backend.services.annotations_parser import AnnotationsParser
from backend.services.data_manager import get_record
from backend.services.json_result import build_result
from backend.services.data_manager import upload_result
from backend.services.s3_operator import upload_images
from backend.services.detection import detect_vehicle
import os

ocr_client = OCRClient()
parser = AnnotationsParser()
image_path=r"/home/ostajanpure/Desktop/ASRS-prod/uploads/R1/DJI_0754 1.jpg"
def process_single_image(image_path):
    annotations = ocr_client.get_annotations(image_path)
    unique_ids = parser.get_unique_ids(annotations)
    records = [get_record(unique_id[0]) for unique_id in unique_ids]
    #record=records[0] if records else None
    for record in records:
    
        
        if record:
            print(record)
            # record is a tuple: (unique_id, text_block)
            # record[0] = unique_id
            # record[1] = text_block (full text where ID was found)
            print(record.unique_id)
            # VIN_NO is not extracted yet - set to empty for now
            print(record.vin_no)
    detection = detect_vehicle(image_path, records)
    image_name = os.path.basename(image_path)
    return unique_ids, record[0]
result = process_single_image(image_path)
print(result)