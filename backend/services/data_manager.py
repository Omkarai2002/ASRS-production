# backend/services/data_manager.py

from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference


# ------------------------------
# Fetch all reports
# ------------------------------
# backend/services/data_manager.py
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.report import Report

def get_reports():
    with SessionLocal() as session:
        return session.query(Report).all()



# ------------------------------
# Create a new report entry
# ------------------------------
def create_report(report_name: str):
    with SessionLocal() as session:
        new_report = Report(name=report_name)
        session.add(new_report)
        session.commit()
        session.refresh(new_report)
        return new_report.id


# ------------------------------
# Delete a report and its inferences
# ------------------------------
def delete_report(report_id: int):
    with SessionLocal() as session:
        # delete inferences first
        session.execute(
            delete(Inference).where(Inference.report_id == report_id)
        )
        # delete report
        session.execute(
            delete(Report).where(Report.id == report_id)
        )
        session.commit()


# ------------------------------
# Fetch all inference rows for a report
# ------------------------------
def get_report_details(report_id: int):
    with SessionLocal() as session:
        stmt = select(Inference).where(Inference.report_id == report_id)
        result = session.execute(stmt).scalars().all()
        return result


# ------------------------------
# Upload inference processing results to DB
# ------------------------------
def upload_result(result_list, report_id, s3_url):
    with SessionLocal() as session:
        for item in result_list:
            db_row = Inference(
                report_id=report_id,
                image_name=item.get("IMG_NAME", ""),
                unique_id=item.get("UNIQUE_ID", ""),
                quantity=item.get("QUANTITY", 1),
                vin_no=item.get("VIN_NO", ""),
                exclusion=item.get("EXCLUSION", ""),
                s3_url=s3_url
            )
            session.add(db_row)
        session.commit()
def get_record(db: Session, report_id: int):
    return db.query(Record).filter(Record.id == report_id).first()


# ---------------------------
# Upload / Save an inference result
# ---------------------------
def upload_result(db: Session, report_id: int, file_name: str, unique_id: str,
                  quantity: int, vin_no: str, exclusion: str, s3_url: str):

    inference = Inference(
        report_id=report_id,
        image_name=file_name,
        unique_id=unique_id,
        quantity=quantity,
        vin_no=vin_no,
        exclusion=exclusion,
        s3_url=s3_url
    )

    db.add(inference)
    db.commit()
    db.refresh(inference)

    return inference
from datetime import date

def get_reports_today():
    with SessionLocal() as session:
        return session.query(Report).filter(Report.createdAt == date.today()).all()
