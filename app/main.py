# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.routers import dashboard, reports, visualize, qr_generation
import os

app = FastAPI(title="ASRS Dashboard")

# Secret key for session cookies
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(visualize.router)
app.include_router(qr_generation.router)

@app.get("/")
def root():
    # Redirect to dashboard if logged in
    return {"message": "Go to /dashboard"}
