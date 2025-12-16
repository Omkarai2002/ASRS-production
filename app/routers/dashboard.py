from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from backend.services.data_manager import get_reports
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    reports_today = get_reports()
    total_reports = len(get_reports())
    qrs_today = len(reports_today)
    system_status = "Active"
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_reports": total_reports,
        "qrs_today": qrs_today,
        "system_status": system_status
    })
