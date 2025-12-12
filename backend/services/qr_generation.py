"""QR Code generation service for VIN numbers"""

import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime


def generate_qr_image(data: str) -> ImageReader:
    """
    Generate QR code image from data string
    
    Args:
        data: The data to encode (e.g., VIN number)
    
    Returns:
        ImageReader object containing QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Convert to image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to ImageReader
    image_bytes = BytesIO()
    qr_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    return ImageReader(image_bytes)


def generate_pdf(vin_no: str, metadata: dict = None) -> bytes:
    """
    Generate a single page PDF with QR code for VIN
    
    Args:
        vin_no: VIN number (17 characters)
        metadata: Optional metadata dictionary
    
    Returns:
        PDF file as bytes
    """
    pdf_buffer = BytesIO()
    
    # Create PDF with letter size
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, height - inch, "QR Code - Vehicle")
    
    # VIN Info
    c.setFont("Helvetica", 12)
    c.drawString(inch, height - 1.5*inch, f"VIN: {vin_no}")
    c.drawString(inch, height - 1.8*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Generate and draw QR code
    qr_image = generate_qr_image(vin_no)
    qr_size = 3 * inch
    
    # Center QR code
    qr_x = (width - qr_size) / 2
    qr_y = (height - qr_size) / 2 - 0.5*inch
    
    c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Footer
    c.setFont("Helvetica", 10)
    c.setFillColor("gray")
    c.drawString(inch, 0.5*inch, "ASRS - Automated Storage & Retrieval System")
    
    c.save()
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()


def generate_bulk_pdf(vin_list: list) -> bytes:
    """
    Generate a PDF with multiple QR codes (one per page)
    
    Args:
        vin_list: List of VIN numbers
    
    Returns:
        PDF file as bytes
    """
    pdf_buffer = BytesIO()
    
    # Create PDF
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    
    for idx, vin_no in enumerate(vin_list):
        if idx > 0:
            c.showPage()  # New page for each VIN
        
        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(inch, height - 0.8*inch, "QR Code - Vehicle")
        
        # VIN Info
        c.setFont("Helvetica", 12)
        c.drawString(inch, height - 1.3*inch, f"VIN: {vin_no}")
        c.drawString(inch, height - 1.6*inch, f"Code {idx + 1} of {len(vin_list)}")
        c.drawString(inch, height - 1.9*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Generate and draw QR code
        qr_image = generate_qr_image(vin_no)
        qr_size = 4 * inch
        
        # Center QR code
        qr_x = (width - qr_size) / 2
        qr_y = (height - qr_size) / 2 - 0.5*inch
        
        c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # Footer
        c.setFont("Helvetica", 9)
        c.setFillColor("gray")
        c.drawString(inch, 0.5*inch, "ASRS - Automated Storage & Retrieval System")
    
    c.save()
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()
