# backend/services/data_manager.py

from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/visualize", response_class=HTMLResponse)
def visualize_reports(request: Request, search: str = None, date: str = None):
    db = SessionLocal()
    try:
        # Start with base query
        query = db.query(Report).order_by(Report.createdAt.desc())
        
        # Apply date filter if provided
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d").date()
                query = query.filter(Report.createdAt == filter_date)
            except ValueError:
                pass
        
        # Get filtered reports
        reports = query.all()
        
        # Get unique dates for date filter (sorted descending)
        unique_dates = db.query(Report.createdAt).distinct().filter(Report.createdAt.isnot(None)).order_by(Report.createdAt.desc()).all()
        unique_dates = [str(d[0]) if d[0] else None for d in unique_dates if d[0]]
        
        return templates.TemplateResponse("visualize.html", {
            "request": request,
            "reports": reports,
            "unique_dates": unique_dates,
            "selected_date": date,
            "search_query": search
        })
    except Exception as e:
        return templates.TemplateResponse("visualize.html", {
            "request": request,
            "reports": [],
            "unique_dates": [],
            "error": f"Error loading reports: {str(e)}"
        })
    finally:
        db.close()

@router.get("/api/report/{report_id}/details")
def get_report_details_api(report_id: int):
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
                    "exclusion": inf.exclusion,
                    "is_non_confirmity": inf.is_non_confirmity,
                    "createdAt": str(inf.createdAt)
                }
                for inf in inferences
            ]
        }
    finally:
        db.close()


# --------------------------
#  REPORTS
# --------------------------

def get_reports(date=None):
    db = SessionLocal()
    try:
        if date:
            return db.query(Report).filter(Report.createdAt == date).all()
        return db.query(Report).all()
    finally:
        db.close()


def get_report(report_id: int):
    db = SessionLocal()
    try:
        return db.query(Report).filter(Report.id == report_id).first()
    finally:
        db.close()


def create_report(report_name: str):
    db = SessionLocal()
    try:
        report = Report(report_name=report_name)
        db.add(report)
        db.commit()
        db.refresh(report)
        return report.id
    finally:
        db.close()


def delete_report(report_id: int):
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            db.delete(report)
            db.commit()
    finally:
        db.close()


# --------------------------
#  INFERENCE HELPERS
# --------------------------

def upload_result(inference_obj: Inference):
    db = SessionLocal()
    try:
        db.add(inference_obj)
        db.commit()
        db.refresh(inference_obj)
        return inference_obj
    finally:
        db.close()


def get_report_details(report_id: int):
    db = SessionLocal()
    try:
        return db.query(Inference).filter(Inference.report_id == report_id).all()
    finally:
        db.close()
