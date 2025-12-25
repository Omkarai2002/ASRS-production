from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import uuid
import logging
from backend.services.data_manager import create_report
from backend.services.inferences import get_inferences

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_BASE = "uploads"  # ensure this exists

@router.get("/upload", response_class=HTMLResponse)
def upload_get(request: Request):
    """Redirect to /reports since upload functionality is consolidated there"""
    if not request.session.get("user"):
        return RedirectResponse("/login")
    return RedirectResponse("/reports", status_code=303)

@router.post("/upload", response_class=HTMLResponse)
async def upload_post(request: Request, report_name: str = Form(...), files: list[UploadFile] = File(...)):
    """
    Handle upload form submission from reports page.
    
    Design:
    - Images from the same user are processed sequentially (maintains order)
    - Different users' uploads are processed in parallel (up to 4 concurrent)
    - Uses global ThreadPoolExecutor to manage concurrent user tasks
    """
    if not request.session.get("user"):
        return RedirectResponse("/login")
    
    user_id = request.session.get("user_id")
    
    try:
        # create DB report entry with user_id
        report_id = create_report(report_name, user_id=user_id)

        # create folder for this report
        safe_name = "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in report_name]).strip().replace(' ', '_')
        report_dir = os.path.join("uploaded_reports", f"{safe_name}_{uuid.uuid4().hex[:8]}")
        os.makedirs(report_dir, exist_ok=True)

        # save files
        for f in files:
            file_path = os.path.join(report_dir, f.filename)
            with open(file_path, "wb") as fh:
                fh.write(await f.read())

        # Submit processing task to global executor
        # This allows multiple users' uploads to process in parallel
        # but within each user's task, images process sequentially
        executor = request.app.state.upload_executor
        future = executor.submit(get_inferences, report_dir, report_id, user_id)
        
        logger.info(f"User {user_id}: Report {report_id} submitted for processing")

        return RedirectResponse(
            url="/reports?success=Report created successfully! Processing has started in background.",
            status_code=303
        )
    except Exception as e:
        logger.error(f"Upload error for user {user_id}: {str(e)}")
        return RedirectResponse(
            url="/reports?error=Failed to create report: " + str(e),
            status_code=303
        )

