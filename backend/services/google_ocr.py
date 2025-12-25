from google.cloud import vision
import os
import cv2
from PIL import Image

class OCRClient:
        
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'GoogleVisionCredential.json'
        self.client = vision.ImageAnnotatorClient()
    
    def get_annotations(self, image_path):
        image = cv2.imread(image_path)
        _, encoded_image = cv2.imencode('.png', image)
        content = encoded_image.tobytes()

        # Send to Google Vision
        response = self.client.text_detection(image=vision.Image(content=content))
        return response.text_annotations


# if __name__ == '__main__':
#     ocr_client = OCRClient()
#     image = cv2.imread('/home/cyrenix/Downloads/IMG-20251117-WA0006.jpg')
#     # image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#     annotations = ocr_client.get_annotations(image)
#     for annotation in annotations:
#         print(annotation.description)
