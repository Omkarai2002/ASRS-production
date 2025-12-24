"""
Database query helpers for ASRS
Centralized, reusable database operations (DRY principle)
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
import logging

from backend.models.report import Report
from backend.models.inference import Inference
from backend.models.user_settings import UserSettings
from backend.database import get_db_context

logger = logging.getLogger(__name__)

# ==================== REPORT QUERIES ====================

def get_user_reports(db: Session, user_id: int, limit: int = None, offset: int = 0) -> List[Report]:
    """Get all reports for a user with inference counts"""
    try:
        query = db.query(
            Report.id,
            Report.report_name,
            Report.createdAt,
            func.count(Inference.id).label('inference_count')
        ).filter(
            Report.user_id == user_id
        ).outerjoin(
            Inference, Report.id == Inference.report_id
        ).group_by(Report.id).order_by(Report.createdAt.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    except Exception as e:
        logger.error(f"Error fetching user reports: {str(e)}")
        raise

def get_report_by_id(db: Session, report_id: int, user_id: int) -> Optional[Report]:
    """Get a specific report, with user_id check for security"""
    try:
        return db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == user_id
        ).first()
    except Exception as e:
        logger.error(f"Error fetching report {report_id}: {str(e)}")
        raise

def get_report_count_for_user(db: Session, user_id: int) -> int:
    """Get total number of reports for a user"""
    try:
        return db.query(Report).filter(Report.user_id == user_id).count()
    except Exception as e:
        logger.error(f"Error counting user reports: {str(e)}")
        raise

# ==================== INFERENCE QUERIES ====================

def get_inferences_by_report(db: Session, report_id: int, user_id: int, 
                            limit: int = None) -> List[Inference]:
    """Get all inferences for a report"""
    try:
        query = db.query(Inference).filter(
            Inference.report_id == report_id,
            Inference.user_id == user_id
        ).order_by(Inference.id.asc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    except Exception as e:
        logger.error(f"Error fetching inferences for report {report_id}: {str(e)}")
        raise

def search_inferences_by_vin(db: Session, user_id: int, vin_no: str) -> List[Inference]:
    """Search inferences by VIN number"""
    try:
        return db.query(Inference).filter(
            Inference.user_id == user_id,
            Inference.vin_no.ilike(f"%{vin_no}%")
        ).all()
    except Exception as e:
        logger.error(f"Error searching by VIN: {str(e)}")
        raise

def search_inferences_by_unique_id(db: Session, user_id: int, unique_id: str) -> List[Inference]:
    """Search inferences by unique ID"""
    try:
        return db.query(Inference).filter(
            Inference.user_id == user_id,
            Inference.unique_id.ilike(f"%{unique_id}%")
        ).all()
    except Exception as e:
        logger.error(f"Error searching by unique ID: {str(e)}")
        raise

def search_inferences(db: Session, user_id: int, query: str, 
                     search_type: str = "all") -> List[Inference]:
    """
    Search inferences by query across VIN or unique_id
    search_type: "all", "vin", "unique_id"
    """
    try:
        base_query = db.query(Inference).filter(Inference.user_id == user_id)
        
        if search_type == "vin":
            return base_query.filter(Inference.vin_no.ilike(f"%{query}%")).all()
        elif search_type == "unique_id":
            return base_query.filter(Inference.unique_id.ilike(f"%{query}%")).all()
        else:  # all
            return base_query.filter(
                (Inference.vin_no.ilike(f"%{query}%")) |
                (Inference.unique_id.ilike(f"%{query}%"))
            ).all()
    except Exception as e:
        logger.error(f"Error searching inferences: {str(e)}")
        raise

def get_inference_count_by_exclusion(db: Session, user_id: int, 
                                    start_date: datetime = None,
                                    end_date: datetime = None) -> Dict[str, int]:
    """Get count of inferences grouped by exclusion status"""
    try:
        query = db.query(
            Inference.exclusion,
            func.count(Inference.id).label('count')
        ).filter(Inference.user_id == user_id)
        
        if start_date:
            query = query.filter(Inference.createdAt >= start_date)
        if end_date:
            query = query.filter(Inference.createdAt <= end_date)
            
        results = query.group_by(Inference.exclusion).all()
        return {result[0]: result[1] for result in results}
    except Exception as e:
        logger.error(f"Error counting inferences by exclusion: {str(e)}")
        raise

# ==================== STATISTICS QUERIES ====================

def get_daily_statistics(db: Session, user_id: int, days: int = 30) -> List[Dict]:
    """Get daily statistics for the last N days"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)
        
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day_reports = db.query(Report).filter(
                Report.user_id == user_id,
                func.date(Report.createdAt) == current_date
            ).count()
            
            day_inferences = db.query(Inference).filter(
                Inference.user_id == user_id,
                func.date(Inference.createdAt) == current_date
            ).count()
            
            daily_data.append({
                "date": current_date.isoformat(),
                "reports": day_reports,
                "items": day_inferences
            })
            
            current_date += timedelta(days=1)
        
        return daily_data
    except Exception as e:
        logger.error(f"Error calculating daily statistics: {str(e)}")
        raise

def get_total_statistics(db: Session, user_id: int) -> Dict[str, int]:
    """Get overall statistics for a user"""
    try:
        total_reports = db.query(Report).filter(Report.user_id == user_id).count()
        total_inferences = db.query(Inference).filter(Inference.user_id == user_id).count()
        today_reports = db.query(Report).filter(
            Report.user_id == user_id,
            func.date(Report.createdAt) == datetime.now().date()
        ).count()
        
        return {
            "total_reports": total_reports,
            "total_inferences": total_inferences,
            "today_reports": today_reports,
        }
    except Exception as e:
        logger.error(f"Error calculating total statistics: {str(e)}")
        raise

# ==================== USER SETTINGS QUERIES ====================

def get_user_settings(db: Session, user_id: int) -> Optional[UserSettings]:
    """Get user settings, return None if not found"""
    try:
        return db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
    except Exception as e:
        logger.error(f"Error fetching user settings: {str(e)}")
        raise

def create_or_update_user_settings(db: Session, user_id: int, 
                                  settings_data: Dict) -> UserSettings:
    """Create or update user settings"""
    try:
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        if user_settings:
            for key, value in settings_data.items():
                if hasattr(user_settings, key):
                    setattr(user_settings, key, value)
            user_settings.updatedAt = datetime.now()
        else:
            user_settings = UserSettings(user_id=user_id, **settings_data)
            db.add(user_settings)
        
        db.commit()
        db.refresh(user_settings)
        return user_settings
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user settings: {str(e)}")
        raise

# ==================== BATCH OPERATIONS ====================

def batch_delete_inferences(db: Session, inference_ids: List[int], user_id: int) -> int:
    """Delete multiple inferences (with user_id check for security)"""
    try:
        deleted = db.query(Inference).filter(
            Inference.id.in_(inference_ids),
            Inference.user_id == user_id
        ).delete(synchronize_session=False)
        
        db.commit()
        return deleted
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting inferences: {str(e)}")
        raise

# ==================== HELPER FUNCTIONS ====================

def get_inference_with_details(db: Session, inference_id: int, user_id: int) -> Optional[Dict]:
    """Get inference with joined report details"""
    try:
        result = db.query(
            Inference,
            Report.report_name
        ).join(
            Report, Inference.report_id == Report.id
        ).filter(
            Inference.id == inference_id,
            Inference.user_id == user_id
        ).first()
        
        if not result:
            return None
            
        inference, report_name = result
        data = {
            **{k: v for k, v in inference.__dict__.items() if not k.startswith('_')},
            "report_name": report_name
        }
        return data
    except Exception as e:
        logger.error(f"Error fetching inference with details: {str(e)}")
        raise
