from google.cloud import vision
import os
import cv2
import io
from PIL import Image
from google.api_core import retry, exceptions

class OCRClient:
        
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'GoogleVisionCredential.json'
        self.client = vision.ImageAnnotatorClient()

    def _get_retry_policy(self):
        return retry.Retry(
            predicate=retry.if_exception_type(
                exceptions.ServiceUnavailable,
                exceptions.GatewayTimeout,
                exceptions.ResourceExhausted,
                exceptions.Aborted,
                exceptions.InternalServerError,
                exceptions.Unknown # GOAWAY with error code 0 might appear as Unknown
            ),
            initial=1.0,
            maximum=60.0,
            multiplier=2.0,
            deadline=120.0,
        )

    def get_annotations(self, image_path):
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        try:
            # Attempt with retry policy
            response = self.client.text_detection(
                image=image,
                retry=self._get_retry_policy()
            )
        except (exceptions.ServiceUnavailable, exceptions.Unknown) as e:
            # If it fails with a connection-like error, try refreshing the client
            print(f"OCR Client encountered error, refreshing client: {e}")
            self.client = vision.ImageAnnotatorClient()
            response = self.client.text_detection(
                image=image,
                retry=self._get_retry_policy()
            )

        annotations = response.text_annotations
        return annotations


# if __name__ == '__main__':
#     ocr_client = OCRClient()
#     image = cv2.imread('/home/cyrenix/Downloads/IMG-20251117-WA0006.jpg')
#     # image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
#     annotations = ocr_client.get_annotations(image)
#     for annotation in annotations:
#         print(annotation.description)
