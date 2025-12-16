# backend/services/data_manager.py

from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/visualize", response_class=HTMLResponse)
def visualize_reports(request: Request, search: str = None, date: str = None, report: int = None):
    db = SessionLocal()
    try:
        # Start with base query
        query = db.query(Report).order_by(Report.createdAt.desc())
        
        # Apply date filter if provided
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d").date()
                query = query.filter(Report.createdAt == filter_date)
            except ValueError:
                pass
        
        # Get filtered reports
        reports = query.all()
        
        # Get unique dates for date filter (sorted descending)
        unique_dates = db.query(Report.createdAt).distinct().filter(Report.createdAt.isnot(None)).order_by(Report.createdAt.desc()).all()
        unique_dates = [str(d[0]) if d[0] else None for d in unique_dates if d[0]]
        
        # Get auto-select report if report ID is provided
        selected_report_id = report
        selected_report_data = None
        if selected_report_id:
            selected_report = db.query(Report).filter(Report.id == selected_report_id).first()
            if selected_report:
                inferences = db.query(Inference).filter(Inference.report_id == selected_report_id).order_by(Inference.id.desc()).all()
                selected_report_data = {
                    "id": selected_report.id,
                    "report_name": selected_report.report_name,
                    "createdAt": str(selected_report.createdAt),
                    "inferences": [
                        {
                            "id": inf.id,
                            "unique_id": inf.unique_id,
                            "vin_no": inf.vin_no,
                            "quantity": inf.quantity,
                            "image_name": inf.image_name,
                            "s3_obj_url": inf.s3_obj_url,
                            "exclusion": inf.exclusion,
                            "is_non_confirmity": inf.is_non_confirmity,
                            "createdAt": str(inf.createdAt)
                        }
                        for inf in inferences
                    ]
                }
        
        return templates.TemplateResponse("visualize.html", {
            "request": request,
            "reports": reports,
            "unique_dates": unique_dates,
            "selected_date": date,
            "search_query": search,
            "selected_report": selected_report_data,
            "selected_report_id": selected_report_id
        })
    except Exception as e:
        return templates.TemplateResponse("visualize.html", {
            "request": request,
            "reports": [],
            "unique_dates": [],
            "error": f"Error loading reports: {str(e)}"
        })
    finally:
        db.close()

@router.get("/api/report/{report_id}/details")
def get_report_details_api(report_id: int):
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"error": "Report not found"}
        
        inferences = db.query(Inference).filter(Inference.report_id == report_id).all()
        
        return {
            "id": report.id,
            "report_name": report.report_name,
            "createdAt": str(report.createdAt),
            "inferences": [
                {
                    "id": inf.id,
                    "unique_id": inf.unique_id,
                    "vin_no": inf.vin_no,
                    "quantity": inf.quantity,
                    "image_name": inf.image_name,
                    "s3_obj_url": inf.s3_obj_url,
                    "exclusion": inf.exclusion,
                    "is_non_confirmity": inf.is_non_confirmity,
                    "createdAt": str(inf.createdAt)
                }
                for inf in inferences
            ]
        }
    finally:
        db.close()


# --------------------------
#  REPORTS
# --------------------------

def get_reports(date=None):
    db = SessionLocal()
    try:
        if date:
            return db.query(Report).filter(Report.createdAt == date).all()
        return db.query(Report).all()
    finally:
        db.close()


def get_report(report_id: int):
    db = SessionLocal()
    try:
        return db.query(Report).filter(Report.id == report_id).first()
    finally:
        db.close()


def create_report(report_name: str):
    db = SessionLocal()
    try:
        report = Report(report_name=report_name)
        db.add(report)
        db.commit()
        db.refresh(report)
        return report.id
    finally:
        db.close()


def delete_report(report_id: int):
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            db.delete(report)
            db.commit()
    finally:
        db.close()


# --------------------------
#  INFERENCE HELPERS
# --------------------------

def upload_result(inference_obj: Inference):
    db = SessionLocal()
    try:
        db.add(inference_obj)
        db.commit()
        db.refresh(inference_obj)
        return inference_obj
    finally:
        db.close()


def get_report_details(report_id: int):
    db = SessionLocal()
    try:
        return db.query(Inference).filter(Inference.report_id == report_id).all()
    finally:
        db.close()


@router.get("/api/report/{report_id}/export/excel")
def export_report_excel(report_id: int):
    """Export report data to Excel file"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"error": "Report not found"}
        
        inferences = db.query(Inference).filter(
            Inference.report_id == report_id
        ).order_by(Inference.id.desc()).all()
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Report Data"
        
        # Define styles
        header_fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Add report header info
        ws['A1'] = f"Report: {report.report_name}"
        ws['A1'].font = Font(bold=True, size=14)
        ws['A2'] = f"Created: {report.createdAt}"
        ws['A2'].font = Font(size=11)
        ws['A3'] = f"Total Items: {len(inferences)}"
        ws['A3'].font = Font(size=11)
        
        # Add blank row
        current_row = 5
        
        # Define headers
        headers = ["Item #", "Unique ID", "VIN Number", "Quantity", "Image Name", "Exclusion", "Non-Conformity", "Created Date", "Download Image"]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
        
        # Add data rows
        for idx, inference in enumerate(inferences, 1):
            row = current_row + idx
            data = [
                idx,
                inference.unique_id or "",
                inference.vin_no or "",
                inference.quantity or 0,
                inference.image_name or "",
                inference.exclusion or "",
                "Yes" if inference.is_non_confirmity else "No",
                str(inference.createdAt) if inference.createdAt else "",
                inference.s3_obj_url or ""
            ]
            
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                cell.value = value
                cell.border = border
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                
                # Make S3 URL a hyperlink in the last column
                if col == len(data) and inference.s3_obj_url:
                    cell.hyperlink = inference.s3_obj_url
                    cell.value = "Download"
                    cell.font = Font(color="0563C1", underline="single")
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 25
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 15
        ws.column_dimensions['H'].width = 20
        ws.column_dimensions['I'].width = 18
        
        # Save to BytesIO
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        return StreamingResponse(
            iter([excel_file.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=Report_{report.id}_{report.report_name.replace(' ', '_')}.xlsx"}
        )
    finally:
        db.close()
