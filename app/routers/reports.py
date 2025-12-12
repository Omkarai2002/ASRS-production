from fastapi import APIRouter, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from backend.services.data_manager import create_report, get_reports, delete_report
from backend.services.inferences import get_inferences
import os
from datetime import datetime
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure folder exists

@router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, search: str = None):
    db = SessionLocal()
    try:
        # Get all reports with their inference counts
        query = db.query(
            Report.id,
            Report.report_name,
            Report.createdAt,
            func.count(Inference.id).label('inference_count')
        ).outerjoin(
            Inference, Report.id == Inference.report_id
        ).group_by(Report.id).order_by(Report.createdAt.desc())
        
        reports = query.all()
        
        # Get unique dates for filtering
        unique_dates = db.query(Report.createdAt).distinct().filter(
            Report.createdAt.isnot(None)
        ).order_by(Report.createdAt.desc()).all()
        unique_dates = [str(d[0]) if d[0] else None for d in unique_dates if d[0]]
        
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "reports": reports,
            "unique_dates": unique_dates,
            "search_query": search
        })
    finally:
        db.close()

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
    db = SessionLocal()
    try:
        # Delete all inferences for this report
        db.query(Inference).filter(Inference.report_id == report_id).delete()
        # Delete the report
        db.query(Report).filter(Report.id == report_id).delete()
        db.commit()
    finally:
        db.close()
    
    return RedirectResponse(url="/reports", status_code=303)

@router.get("/api/report/{report_id}")
def get_report_api(report_id: int):
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"error": "Report not found"}
        
        inferences = db.query(Inference).filter(Inference.report_id == report_id).all()
        
        return {
            "id": report.id,
            "report_name": report.report_name,
            "createdAt": str(report.createdAt),
            "inferences": [
                {
                    "id": inf.id,
                    "unique_id": inf.unique_id,
                    "vin_no": inf.vin_no,
                    "quantity": inf.quantity,
                    "image_name": inf.image_name,
                    "s3_obj_url": inf.s3_obj_url,
                }
                for inf in inferences
            ]
        }
    finally:
        db.close()
