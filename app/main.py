from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from concurrent.futures import ThreadPoolExecutor
import os
import logging

from .routers import dashboard, reports, upload, visualize, auth_routes, qr_generation, settings, search

logger = logging.getLogger(__name__)

app = FastAPI()
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Global ThreadPoolExecutor for managing concurrent user uploads
# Max 4 users can have their reports processing simultaneously
# Within each user's task, images process sequentially
app.state.upload_executor = ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="upload_worker_"
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(upload.router)
app.include_router(visualize.router)
app.include_router(qr_generation.router)
app.include_router(settings.router)
app.include_router(search.router)

@app.get("/", include_in_schema=False)
def root(request: Request):
    """Redirect to dashboard if logged in, else to login"""
    if request.session.get("user"):
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")

@app.on_event("shutdown")
def shutdown_executor():
    """Gracefully shutdown the upload executor on app shutdown"""
    logger.info("Shutting down upload executor...")
    app.state.upload_executor.shutdown(wait=True)
    logger.info("Upload executor shutdown complete")

