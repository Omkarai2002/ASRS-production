from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/visualize", response_class=HTMLResponse)
def visualize_reports():
    if not os.path.exists("reports.html"):
        return "<h2>No reports found for visualization.</h2>"

    with open("reports.html", "r") as file:
        return file.read()
