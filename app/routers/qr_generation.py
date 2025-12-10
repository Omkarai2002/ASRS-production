from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from backend.services.qr_generation import generate_pdf

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/qr", response_class=HTMLResponse)
def qr_page(request: Request):
    return templates.TemplateResponse("qr_generation.html", {"request": request})

@router.post("/qr/generate")
def generate_qr(request: Request, vin_no: str = Form(...)):
    pdf_bytes = generate_pdf(vin_no, None)
    pdf_path = f"temp/QR_{vin_no}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"QR_{vin_no}.pdf")
