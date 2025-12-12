from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth.auth import authenticate_user, create_user, get_user_by_username

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Display login page"""
    if request.session.get("user"):
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login submission"""
    user = authenticate_user(username, password)
    
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password",
            },
            status_code=401,
        )
    
    # Store user in session
    request.session["user"] = username
    request.session["user_id"] = user.id
    
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    """Display signup page"""
    if request.session.get("user"):
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})


@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Handle signup submission"""
    
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Passwords do not match",
            },
            status_code=400,
        )
    
    # Validate password length
    if len(password) < 6:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Password must be at least 6 characters",
            },
            status_code=400,
        )
    
    # Check if user already exists
    existing_user = get_user_by_username(username)
    if existing_user:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Username already exists",
            },
            status_code=400,
        )
    
    # Create new user
    try:
        user = create_user(username, password)
        
        # Auto-login after signup
        request.session["user"] = username
        request.session["user_id"] = user.id
        
        return RedirectResponse("/dashboard", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": f"Error creating account: {str(e)}",
            },
            status_code=500,
        )


@router.get("/logout")
def logout(request: Request):
    """Handle logout"""
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
