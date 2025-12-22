from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.database import SessionLocal
from backend.models.user_settings import UserSettings
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    """Display user settings page"""
    # Check if user is logged in
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        # Get or create user settings
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not user_settings:
            # Create default settings for new user
            user_settings = UserSettings(
                user_id=user_id,
                images_per_row=8,
                level_prefix="L",
                image_size="medium",
                show_image_info=True,
                show_level_info=True
            )
            db.add(user_settings)
            db.commit()

        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": user_settings,
            "username": request.session.get("user"),
            "message": None
        })
    except Exception as e:
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": None,
            "username": request.session.get("user"),
            "error": str(e)
        })
    finally:
        db.close()


@router.post("/settings/update")
async def update_settings(
    request: Request,
    images_per_row: str = Form(...),
    level_prefix: str = Form(...),
    image_size: str = Form(...),
    show_image_info: bool = Form(False),
    show_level_info: bool = Form(False)
):
    """Update user settings"""
    # Check if user is logged in
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        # Parse images_per_row
        try:
            images_per_row_int = int(images_per_row)
            if images_per_row_int < 1 or images_per_row_int > 20:
                images_per_row_int = 8
        except (ValueError, TypeError):
            images_per_row_int = 8

        # Get or create user settings
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not user_settings:
            user_settings = UserSettings(user_id=user_id)
        
        # Update settings
        user_settings.images_per_row = images_per_row_int
        user_settings.level_prefix = level_prefix.strip() or "L"
        user_settings.image_size = image_size
        user_settings.show_image_info = show_image_info
        user_settings.show_level_info = show_level_info
        user_settings.updatedAt = datetime.utcnow()
        
        db.add(user_settings)
        db.commit()

        return RedirectResponse(
            url="/settings?success=Settings updated successfully!",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url="/settings?error=Failed to update settings: " + str(e),
            status_code=303
        )
    finally:
        db.close()
