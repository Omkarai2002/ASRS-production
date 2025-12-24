from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from backend.database import SessionLocal
from backend.models.inference import Inference
from backend.models.report import Report
from backend.models.user_settings import UserSettings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db() -> Session:
    """Database session context manager"""
    db = SessionLocal()
    return db


def close_db(db: Session):
    """Close database session"""
    if db:
        db.close()


@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request):
    """Display search page"""
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse("search.html", {"request": request})


@router.get("/api/search")
def search_items(
    request: Request,
    query: str = Query("", min_length=1),
    search_type: str = Query("all", regex="^(vin|unique_id|all)$")
):
    """
    Search for items by VIN number, Unique ID, or both
    Returns: List of matching inferences with their details
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    if not query or len(query.strip()) == 0:
        return JSONResponse({"error": "Search query cannot be empty"}, status_code=400)
    
    db = get_db()
    try:
        search_query = query.strip()
        
        # Build the base query with user isolation
        base_query = db.query(
            Inference.id,
            Inference.unique_id,
            Inference.image_name,
            Inference.vin_no,
            Inference.quantity,
            Inference.exclusion,
            Inference.createdAt,
            Inference.s3_obj_url,
            Inference.report_id,
            Report.report_name
        ).join(
            Report, Inference.report_id == Report.id
        ).filter(
            Inference.user_id == user_id
        )
        
        # Apply search filters
        if search_type == "vin":
            results = base_query.filter(
                Inference.vin_no.ilike(f"%{search_query}%")
            ).all()
        elif search_type == "unique_id":
            results = base_query.filter(
                Inference.unique_id.ilike(f"%{search_query}%")
            ).all()
        else:  # all
            results = base_query.filter(
                (Inference.vin_no.ilike(f"%{search_query}%")) |
                (Inference.unique_id.ilike(f"%{search_query}%"))
            ).all()
        
        if not results:
            return JSONResponse({
                "items": [],
                "count": 0,
                "message": "No items found matching your search"
            })
        
        # Get user settings for location calculation
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        images_per_row = user_settings.images_per_row if user_settings else 5
        level_prefix = user_settings.level_prefix if user_settings else "L"
        
        # Format results with location information
        items = []
        for idx, result in enumerate(results):
            # Calculate location
            level_number = (idx // images_per_row) + 1
            position_in_level = (idx % images_per_row) + 1
            location = f"{level_prefix}{level_number}-{position_in_level}"
            
            item_data = {
                "id": result.id,
                "unique_id": result.unique_id,
                "vin_no": result.vin_no,
                "image_name": result.image_name,
                "quantity": result.quantity,
                "exclusion": result.exclusion,
                "createdAt": result.createdAt.strftime("%Y-%m-%d %H:%M:%S") if result.createdAt else "N/A",
                "date_only": result.createdAt.strftime("%Y-%m-%d") if result.createdAt else "N/A",
                "s3_obj_url": result.s3_obj_url,
                "report_name": result.report_name,
                "report_id": result.report_id,
                "location": location,
                "level_number": level_number,
                "position_in_level": position_in_level
            }
            items.append(item_data)
        
        return JSONResponse({
            "items": items,
            "count": len(items),
            "search_query": search_query,
            "search_type": search_type
        })
    
    except Exception as e:
        return JSONResponse(
            {"error": f"Search failed: {str(e)}"},
            status_code=500
        )
    finally:
        close_db(db)


@router.get("/api/item/{item_id}")
def get_item_details(request: Request, item_id: int):
    """
    Get detailed information about a specific item including all its occurrences
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    db = get_db()
    try:
        # Get the specific item
        item = db.query(Inference).filter(
            Inference.id == item_id,
            Inference.user_id == user_id
        ).first()
        
        if not item:
            return JSONResponse({"error": "Item not found"}, status_code=404)
        
        # Get all occurrences of this item (by unique_id or vin_no)
        all_occurrences = []
        
        if item.unique_id:
            all_occurrences = db.query(
                Inference.id,
                Inference.unique_id,
                Inference.vin_no,
                Inference.image_name,
                Inference.exclusion,
                Inference.createdAt,
                Inference.s3_obj_url,
                Report.report_name
            ).join(
                Report, Inference.report_id == Report.id
            ).filter(
                Inference.user_id == user_id,
                Inference.unique_id == item.unique_id
            ).order_by(Inference.createdAt.desc()).all()
        
        # Get user settings
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        images_per_row = user_settings.images_per_row if user_settings else 5
        level_prefix = user_settings.level_prefix if user_settings else "L"
        
        # Format occurrences with location
        occurrences = []
        for idx, occurrence in enumerate(all_occurrences):
            level_number = (idx // images_per_row) + 1
            position_in_level = (idx % images_per_row) + 1
            location = f"{level_prefix}{level_number}-{position_in_level}"
            
            occurrences.append({
                "id": occurrence.id,
                "location": location,
                "date": occurrence.createdAt.strftime("%Y-%m-%d %H:%M:%S") if occurrence.createdAt else "N/A",
                "image_url": occurrence.s3_obj_url,
                "report_name": occurrence.report_name,
                "exclusion": occurrence.exclusion,
                "image_name": occurrence.image_name
            })
        
        return JSONResponse({
            "item": {
                "id": item.id,
                "unique_id": item.unique_id,
                "vin_no": item.vin_no,
                "image_name": item.image_name,
                "quantity": item.quantity,
                "exclusion": item.exclusion,
                "createdAt": item.createdAt.strftime("%Y-%m-%d %H:%M:%S") if item.createdAt else "N/A",
                "s3_obj_url": item.s3_obj_url
            },
            "occurrences": occurrences,
            "occurrence_count": len(occurrences)
        })
    
    except Exception as e:
        return JSONResponse(
            {"error": f"Failed to get item details: {str(e)}"},
            status_code=500
        )
    finally:
        close_db(db)
