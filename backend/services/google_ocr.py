from google.cloud import vision
import os
import cv2
import io
from PIL import Image

class OCRClient:
        
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'GoogleVisionCredential.json'
        self.client = vision.ImageAnnotatorClient()
    
    def get_annotations(self, image_path):
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        response = self.client.text_detection(image=vision.Image(content=content))
        annotations = response.text_annotations
        return annotations


# if __name__ == '__main__':
#     ocr_client = OCRClient()
#     image = cv2.imread('/home/cyrenix/Downloads/IMG-20251117-WA0006.jpg')
#     # image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#     annotations = ocr_client.get_annotations(image)
#     for annotation in annotations:
#         print(annotation.description)
