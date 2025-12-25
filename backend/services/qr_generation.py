"""QR Code generation service for VIN numbers"""

import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime


from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from backend.services.data_manager import insert_raw_data

def draw_qr_page(c, vin_no, unique_id):
    """
    Draws a single page with QR code on the given canvas.
    Adapted from user snippet.
    """
    page_width, page_height = A4

    # ---- BORDER ----
    margin = 7 * mm
    c.setLineWidth(3)
    c.rect(margin, margin, page_width - 2 * margin, page_height - 2 * margin)

    # ---- VIN NO (top text) ----
    vin_font_size = 40
    c.setFont("Helvetica-Bold", vin_font_size)
    
    text_width = stringWidth(str(vin_no), "Helvetica-Bold", vin_font_size)
    c.drawString((page_width - text_width) / 2, page_height - 40 * mm, str(vin_no))

    # ---- QR CODE ----
    qr_size = 180 * mm  # large QR
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(f"VIN NO: {vin_no} UNIQUE ID: {unique_id}")
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    qr_x = (page_width - qr_size) / 2
    qr_y = (page_height / 2) - (qr_size / 2)
    c.drawImage(ImageReader(img), qr_x, qr_y, qr_size, qr_size)

    # ---- UNIQUE ID (bottom text) ----
    uid_font_size = 115
    c.setFont("Helvetica-Bold", uid_font_size)
    uid_text_width = stringWidth(unique_id, "Helvetica-Bold", uid_font_size)

    # Auto-scale text if it's too wide
    available_width = page_width - 2 * margin - 10 * mm
    if uid_text_width > available_width:
        scale_factor = available_width / uid_text_width
        uid_font_size *= scale_factor
        c.setFont("Helvetica-Bold", uid_font_size)
        uid_text_width = stringWidth(unique_id, "Helvetica-Bold", uid_font_size)

    c.drawString((page_width - uid_text_width) / 2, margin + 20 * mm, unique_id)

def generate_pdf(vin_no: str, unique_id: str) -> bytes:
    """
    Generate a two-page PDF with QR code for VIN/UID
    """
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # First Copy
    draw_qr_page(c, vin_no, unique_id)
    c.showPage()
    
    # Second Copy
    draw_qr_page(c, vin_no, unique_id)
    c.showPage()
    
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def generate_bulk_pdf(vin_list: list, date_val, user_id: int) -> bytes:
    """
    Generates a multi-page PDF with QR codes for each VIN.
    Inserts data into DB for each VIN.
    """
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    for vin_no in vin_list:
        unique_id = insert_raw_data(vin_no, date_val, user_id)
        
        # First Copy
        draw_qr_page(c, vin_no, unique_id)
        c.showPage()
        
        # Second Copy
        draw_qr_page(c, vin_no, unique_id)
        c.showPage()
    
    c.save()
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()
