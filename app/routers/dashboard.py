from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from datetime import datetime, date
from sqlalchemy import func, and_
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, from_date: str = None, to_date: str = None, report_id: str = None):
    """Display interactive dashboard with user-specific statistics, filters, and pie chart"""
    # Check if user is logged in
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
   
    db = SessionLocal()
    try:
        # Parse date filters
        from_dt = None
        to_dt = None
        if from_date:
            try:
                from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
            except:
                pass
        if to_date:
            try:
                to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
            except:
                pass
        
        # Parse report_id filter (can be empty string)
        report_id_filter = None
        if report_id and report_id.strip():
            try:
                report_id_filter = int(report_id)
            except (ValueError, TypeError):
                pass
        
        # Build base query with user_id filter
        reports_query = db.query(Report).filter(Report.user_id == user_id)
        inferences_query = db.query(Inference).filter(Inference.user_id == user_id)
        
        # Apply date filters
        if from_dt:
            reports_query = reports_query.filter(func.date(Report.createdAt) >= from_dt)
            inferences_query = inferences_query.filter(func.date(Inference.createdAt) >= from_dt)
        if to_dt:
            reports_query = reports_query.filter(func.date(Report.createdAt) <= to_dt)
            inferences_query = inferences_query.filter(func.date(Inference.createdAt) <= to_dt)
        
        # Apply specific report filter if selected
        if report_id_filter:
            reports_query = reports_query.filter(Report.id == report_id_filter)
            inferences_query = inferences_query.filter(Inference.report_id == report_id_filter)
        
        # Get filtered data
        user_reports = reports_query.all()
        user_inferences = inferences_query.all()
        
        # Calculate basic statistics
        total_reports = len(user_reports)
        items_detected = len(user_inferences)
        
        # Calculate exclusion breakdown for pie chart
        exclusion_stats = {
            "empty_skid": 0,
            "sticker_not_found": 0,
            "multiple_stickers": 0,
            "filled": 0
        }
        
        for inference in user_inferences:
            exclusion = inference.exclusion or ""
            if exclusion.strip() == "":
                # Empty exclusion means it was successfully processed (filled)
                exclusion_stats["filled"] += 1
            elif "Empty Skid" in exclusion:
                exclusion_stats["empty_skid"] += 1
            elif "Sticker not found" in exclusion:
                exclusion_stats["sticker_not_found"] += 1
            elif "Multiple stickers" in exclusion:
                exclusion_stats["multiple_stickers"] += 1
        
        # Get today's count
        today = date.today()
        reports_today = db.query(Report).filter(
            Report.user_id == user_id,
            func.date(Report.createdAt) == today
        ).count()
        
        # Get all user's reports for dropdown filter
        all_user_reports = db.query(Report).filter(Report.user_id == user_id).order_by(Report.createdAt.desc()).all()
        
        # Calculate daily statistics for line graph (last 30 days)
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=29)  # Last 30 days
        
        daily_data = []
        current_date = start_date
        while current_date <= end_date:
            day_reports = db.query(Report).filter(
                Report.user_id == user_id,
                func.date(Report.createdAt) == current_date
            ).count()
            day_inferences = db.query(Inference).filter(
                Inference.user_id == user_id,
                func.date(Inference.createdAt) == current_date
            ).count()
            
            daily_data.append({
                "date": str(current_date),
                "reports": day_reports,
                "items": day_inferences
            })
            current_date += timedelta(days=1)
        
        system_status = "Active"
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_reports": total_reports,
            "qrs_today": items_detected,
            "reports_today": reports_today,
            "system_status": system_status,
            "username": request.session.get("user"),
            "from_date": from_date,
            "to_date": to_date,
            "selected_report_id": report_id_filter,
            "all_reports": all_user_reports,
            "exclusion_stats": exclusion_stats,
            "exclusion_stats_json": json.dumps(exclusion_stats),
            "daily_data": daily_data,
            "daily_data_json": json.dumps(daily_data)
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_reports": 0,
            "qrs_today": 0,
            "reports_today": 0,
            "system_status": "Error",
            "error": str(e),
            "exclusion_stats": {"empty_skid": 0, "sticker_not_found": 0, "multiple_stickers": 0, "filled": 0},
            "exclusion_stats_json": json.dumps({"empty_skid": 0, "sticker_not_found": 0, "multiple_stickers": 0, "filled": 0}),
            "all_reports": [],
            "daily_data": [],
            "daily_data_json": json.dumps([])
        })
    finally:
        db.close()
