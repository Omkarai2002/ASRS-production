from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from datetime import datetime, date
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Display dashboard with user-specific statistics"""
    # Check if user is logged in
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    
    db = SessionLocal()
    try:
        # Get ONLY this user's reports
        user_reports = db.query(Report).filter(Report.user_id == user_id).all()
        
        # Get ONLY this user's inferences
        user_inferences = db.query(Inference).filter(Inference.user_id == user_id).all()
        
        # Get reports created TODAY by this user
        today = date.today()
        reports_today = db.query(Report).filter(
            Report.user_id == user_id,
            func.date(Report.createdAt) == today
        ).count()
        
        # Calculate statistics
        total_reports = len(user_reports)
        items_detected = len(user_inferences)
        system_status = "Active"
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_reports": total_reports,
            "qrs_today": items_detected,
            "reports_today": reports_today,
            "system_status": system_status,
            "username": request.session.get("user")  # Optional: Show username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_reports": 0,
            "qrs_today": 0,
            "reports_today": 0,
            "system_status": "Error",
            "error": str(e)
        })
    finally:
        db.close()
