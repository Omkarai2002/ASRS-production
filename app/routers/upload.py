from fastapi import APIRouter, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import uuid
from services.data_manager import create_report
from services.inference import get_inferences

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_BASE = "uploads"  # ensure this exists

@router.get("/upload", response_class=HTMLResponse)
def upload_get(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    return templates.TemplateResponse("upload.html", {"request": request, "error": None})

@router.post("/upload", response_class=HTMLResponse)
async def upload_post(request: Request, background_tasks: BackgroundTasks,
                      report_name: str = Form(...), files: list[UploadFile] = File(...)):
    if not request.session.get("user"):
        return RedirectResponse("/login")
    # create DB report entry
    report_id = create_report(report_name)

    # create folder for this report
    safe_name = "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in report_name]).strip().replace(' ', '_')
    report_dir = os.path.join("uploaded_reports", f"{safe_name}_{uuid.uuid4().hex[:8]}")
    os.makedirs(report_dir, exist_ok=True)

    # save files
    for f in files:
        file_path = os.path.join(report_dir, f.filename)
        with open(file_path, "wb") as fh:
            fh.write(await f.read())

    # run background inference (non-blocking)
    background_tasks.add_task(get_inferences, report_dir, report_id)

    return templates.TemplateResponse("upload.html", {"request": request, "info": f"Report created ({report_id}). Processing started in background."})
