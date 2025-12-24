from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.services.qr_generation import generate_pdf, generate_bulk_pdf
import os
import io

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/qr", response_class=HTMLResponse)
def qr_page(request: Request):
    """Display QR generation page"""
    return templates.TemplateResponse("qr_generation.html", {"request": request})


@router.post("/qr/generate")
async def generate_qr(
    request: Request, 
    vin_no: str = Form(...), 
    date: str = Form(None),
    action: str = Form("download")  # "download" or "print"
):
    """Generate QR code for single VIN"""
    try:
        user_id = request.session.get("user_id")
        user_id = int(user_id)
        if not user_id:
            return RedirectResponse("/login", status_code=303)

        # Validate VIN
        vin_no = vin_no.strip().upper()

        # Handle Date
        from datetime import datetime
        if not date:
            date_val = datetime.now().date()
        else:
            try:
                date_val = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                date_val = datetime.now().date()

        # Insert Data
        from backend.services.data_manager import insert_raw_data
        unique_id = insert_raw_data(vin_no, date_val, user_id)
        print(unique_id)

        # Generate PDF
        pdf_bytes = generate_pdf(vin_no, unique_id)
        
        # Determine disposition based on action
        if action == "print":
            disposition = "inline"  # Opens in browser for printing
        else:
            disposition = f"attachment; filename=QR_Report_{vin_no}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": disposition}
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
async def generate_bulk_qr(
    request: Request, 
    vins: str = Form(None),
    date: str = Form(None),
    action: str = Form("download")  # "download" or "print"
):
    """Generate QR codes for multiple VINs as a bulk PDF"""
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse("/login", status_code=303)

        # Parse VINs
        if not vins:
             return templates.TemplateResponse(
                "qr_generation.html",
                {"request": request, "error": "Please provide VINs"},
                status_code=400,
            )
            
        vin_list = [v.strip().upper() for v in vins.strip().split('\n') if v.strip()]
        
        # Validate VINs
        if not vin_list:
            return templates.TemplateResponse(
                "qr_generation.html",
                {"request": request, "error": "Please enter at least one VIN"},
                status_code=400,
            )
        
        # Handle Date
        from datetime import datetime
        if not date:
            date_val = datetime.now().date()
        else:
            try:
                date_val = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                date_val = datetime.now().date()
        
        # Generate bulk PDF
        pdf_bytes = generate_bulk_pdf(vin_list, date_val, user_id)
        
        # Determine disposition based on action
        if action == "print":
            disposition = "inline"  # Opens in browser for printing
        else:
            disposition = f"attachment; filename=QR_Bulk_{len(vin_list)}_codes.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": disposition}
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