from fastapi import APIRouter, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from backend.services.data_manager import create_report
from backend.services.inferences import get_inferences

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db() -> Session:
    """Database session context manager"""
    db = SessionLocal()
    return db


def close_db(db: Session):
    """Close database session"""
    if db:
        db.close()


@router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, search: str = None):
    """Display all reports with search capability"""
    db = get_db()
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
        
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "reports": reports,
            "search_query": search
        })
    except Exception as e:
        return templates.TemplateResponse(
            "reports.html",
            {"request": request, "reports": [], "error": str(e)},
            status_code=500
        )
    finally:
        close_db(db)


@router.post("/reports/create")
async def create_report_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    report_name: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """Create a new report with file uploads"""
    try:
        if not report_name or not report_name.strip():
            return RedirectResponse(url="/reports?error=Report name is required", status_code=303)
        
        if not files or len(files) == 0:
            return RedirectResponse(url="/reports?error=At least one file is required", status_code=303)

        # Sanitize folder name
        safe_name = "".join([
            c if c.isalnum() or c in (' ', '-', '_') else '_' 
            for c in report_name
        ]).strip()
        
        report_dir = os.path.join(UPLOAD_DIR, safe_name)
        os.makedirs(report_dir, exist_ok=True)

        # Save uploaded files
        for file in files:
            if file.filename:
                file_path = os.path.join(report_dir, file.filename)
                with open(file_path, "wb") as f:
                    f.write(await file.read())

        # Create report in database
        report_id = create_report(report_name)

        # Queue background image processing task
        background_tasks.add_task(get_inferences, report_dir, report_id)

        return RedirectResponse(url="/reports?success=Report created successfully", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/reports?error=Error creating report: {str(e)}", status_code=303)


@router.post("/reports/{report_id}/delete")
def delete_report_endpoint(report_id: int):
    """Delete a report and all associated inferences"""
    db = get_db()
    try:
        # Delete all inferences associated with this report
        db.query(Inference).filter(Inference.report_id == report_id).delete()
        
        # Delete the report
        db.query(Report).filter(Report.id == report_id).delete()
        
        db.commit()
        return RedirectResponse(url="/reports?success=Report deleted successfully", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/reports?error=Error deleting report: {str(e)}", status_code=303)
    finally:
        close_db(db)


@router.get("/api/report/{report_id}")
def get_report_api(report_id: int):
    """API endpoint to get report details with inferences"""
    db = get_db()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"error": "Report not found", "status": 404}
        
        inferences = db.query(Inference).filter(
            Inference.report_id == report_id
        ).order_by(Inference.id.desc()).all()
        
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
    except Exception as e:
        return {"error": str(e), "status": 500}
    finally:
        close_db(db)
