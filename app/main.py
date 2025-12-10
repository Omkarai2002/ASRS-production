# app/main.py
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .models import create_db_and_tables, engine, User
from .auth import create_user, authenticate_user, get_user_by_username

import os

app = FastAPI()
# secret key for session cookies - in production keep this secret (env var)
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")  # optional

# ensure DB exists
create_db_and_tables()

# ---------- helpers ----------
def is_logged_in(request: Request):
    return "user" in request.session

def get_current_username(request: Request):
    return request.session.get("user")

# ---------- routes ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if is_logged_in(request):
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")

@app.get("/signup", response_class=HTMLResponse)
def signup_get(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})

@app.post("/signup", response_class=HTMLResponse)
def signup_post(request: Request, username: str = Form(...), password: str = Form(...), confirm: str = Form(...)):
    # simple validation
    if password != confirm:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Passwords do not match."})
    if get_user_by_username(username):
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already taken."})
    create_user(username, password)
    # redirect to login after signup
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials."})
    # login success -> store username in session
    request.session["user"] = user.username
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/login")
    username = get_current_username(request)
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")
