from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from backend.services.data_manager import get_reports, get_report_details,get_reports_today

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/visualize", response_class=HTMLResponse)
def visualize(request: Request, report_id: int = None):
    if report_id:
        details = get_report_details(report_id)
        return templates.TemplateResponse("visualize_detail.html", {
            "request": request,
            "report_id": report_id,
            "details": details
        })
    
    reports = get_reports_today()
    return templates.TemplateResponse("visualize.html", {
        "request": request,
        "reports": reports
    })
