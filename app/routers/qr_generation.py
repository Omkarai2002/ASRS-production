from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from backend.services.qr_generation import generate_pdf, generate_bulk_pdf
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/qr", response_class=HTMLResponse)
def qr_page(request: Request):
    """Display QR generation page"""
    return templates.TemplateResponse("qr_generation.html", {"request": request})


@router.post("/qr/generate")
async def generate_qr(request: Request, vin_no: str = Form(...)):
    """Generate QR code for single VIN"""
    try:
        # Validate VIN
        vin_no = vin_no.strip().upper()
        if len(vin_no) != 17:
            return templates.TemplateResponse(
                "qr_generation.html",
                {"request": request, "error": "VIN must be exactly 17 characters"},
                status_code=400,
            )

        # Generate PDF
        pdf_bytes = generate_pdf(vin_no, None)
        
        # Save temporarily
        os.makedirs("temp", exist_ok=True)
        pdf_path = f"temp/QR_{vin_no}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"QR_{vin_no}.pdf",
        )
    except Exception as e:
        return templates.TemplateResponse(
            "qr_generation.html",
            {
                "request": request,
                "error": f"Error generating QR code: {str(e)}",
            },
            status_code=500,
        )


@router.post("/qr/generate-bulk")
async def generate_bulk_qr(request: Request, vins: str = Form(...)):
    """Generate QR codes for multiple VINs as a bulk PDF"""
    try:
        # Parse VINs
        vin_list = [v.strip().upper() for v in vins.strip().split('\n') if v.strip()]
        
        # Validate VINs
        if not vin_list:
            return templates.TemplateResponse(
                "qr_generation.html",
                {"request": request, "error": "Please enter at least one VIN"},
                status_code=400,
            )
        
        invalid_vins = [v for v in vin_list if len(v) != 17]
        if invalid_vins:
            return templates.TemplateResponse(
                "qr_generation.html",
                {
                    "request": request,
                    "error": f"Invalid VINs (must be 17 chars): {', '.join(invalid_vins[:3])}...",
                },
                status_code=400,
            )
        
        # Generate bulk PDF
        pdf_bytes = generate_bulk_pdf(vin_list)
        
        # Save temporarily
        os.makedirs("temp", exist_ok=True)
        pdf_path = f"temp/QR_Bulk_{len(vin_list)}_codes.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"QR_Bulk_{len(vin_list)}_codes.pdf",
        )
    except Exception as e:
        return templates.TemplateResponse(
            "qr_generation.html",
            {
                "request": request,
                "error": f"Error generating QR codes: {str(e)}",
            },
            status_code=500,
        )
