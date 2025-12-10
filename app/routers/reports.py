from fastapi import APIRouter, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.services.data_manager import create_report, get_reports, delete_report
from backend.services.inferences import get_inferences
import os
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure folder exists

@router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    reports = get_reports(None)  # Get all reports
    return templates.TemplateResponse("reports.html", {"request": request, "reports": reports})

@router.post("/reports/create")
async def create_report_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    report_name: str = Form(...),
    files: list[UploadFile] = File(...)
):
    # Sanitize folder name
    safe_name = "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in report_name]).strip()
    report_dir = os.path.join(UPLOAD_DIR, safe_name)
    os.makedirs(report_dir, exist_ok=True)

    # Save files
    for file in files:
        file_path = os.path.join(report_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

    # Create report in DB
    report_id = create_report(report_name)

    # Process images in background
    background_tasks.add_task(get_inferences, report_dir, report_id)

    return RedirectResponse(url="/reports", status_code=303)

@router.post("/reports/{report_id}/delete")
def delete_report_endpoint(report_id: int):
    delete_report(report_id)
    return RedirectResponse(url="/reports", status_code=303)
