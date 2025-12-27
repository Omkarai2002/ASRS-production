import os
import boto3
import uuid
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
import io
 
# Load variables from .env file
load_dotenv()
 
# Set AWS credentials directly from environment variables
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("aws_access_key_id")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("aws_secret_access_key")
os.environ["AWS_DEFAULT_REGION"] = os.getenv("region_name")
 
# Constants
BUCKET_NAME = os.getenv("s3_bucket_name")
S3_BASE_FOLDER = "uploads"

# Compression settings
MAX_IMAGE_SIZE = (1920, 1080)  # Max resolution
JPEG_QUALITY = 85  # Quality 1-100, 85 is good balance
 
def compress_image(image_path, output_path=None):
    """
    Compress image while maintaining aspect ratio and quality.
    
    Args:
        image_path: Path to the original image
        output_path: Path to save compressed image (if None, overwrites original)
    
    Returns:
        Path to compressed image
    """
    try:
        # Open image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if larger than max size (maintains aspect ratio)
        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Prepare output path
        if output_path is None:
            output_path = image_path
        
        # Save with compression
        img.save(output_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
        
        return output_path
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")
        return image_path  # Return original if compression fails
 
def upload_images(image_path):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    s3_folder = f"{S3_BASE_FOLDER}/"
    s3 = boto3.client('s3')
    image_name = os.path.basename(image_path)

    # Compress image before upload
    try:
        # Create temporary compressed file path
        compressed_path = image_path + ".compressed.jpg"
        compress_image(image_path, compressed_path)
        upload_file = compressed_path
    except Exception as e:
        print(f"Compression failed for {image_name}, uploading original: {e}")
        upload_file = image_path

    s3_key = s3_folder + f"compressed_{timestamp}_{str(uuid.uuid1())}_{image_name}"
    try:
        s3.upload_file(upload_file, BUCKET_NAME, s3_key)
        region = os.getenv("region_name")
        s3_url = f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{s3_key}"
        
        # Clean up temporary compressed file
        if upload_file != image_path and os.path.exists(upload_file):
            os.remove(upload_file)
        
        return s3_key, s3_url
    except Exception as e:
        print(f"Failed to upload {image_name}: {e}")
        # Clean up on failure too
        if upload_file != image_path and os.path.exists(upload_file):
            os.remove(upload_file)
        return None, None

if __name__ == "__main__":
    s3_key, s3_url = upload_images("./testing images/debug/DJI_0485.JPG")
    print(s3_url)
            
 
 
