from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from urllib3 import request
from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from backend.models.raw_data import RawData

def get_reports():
    with SessionLocal() as session:
        return session.query(Report).all()

def get_record(unique_id: str):
    with SessionLocal() as session:
        stmt = select(RawData).where(RawData.unique_id == unique_id)
        return session.execute(stmt).scalars().first()
def get_reports_today():
    with SessionLocal() as session:
        return session.query(Report).filter(func.date(Report.createdAt) == date.today()).all()


def create_report(report_name: str, user_id: int = None):
    with SessionLocal() as session:
        report = Report(report_name=report_name, user_id=user_id)
        session.add(report)
        session.commit()
        session.refresh(report)
        return report.id


def delete_report(report_id: int):
    with SessionLocal() as session:
        session.query(Inference).filter(Inference.report_id == report_id).delete(synchronize_session=False)
        session.query(Report).filter(Report.id == report_id).delete(synchronize_session=False)
        session.commit()


def get_report_details(report_id: int):
    with SessionLocal() as session:
        stmt = select(Inference).where(Inference.report_id == report_id)
        return session.execute(stmt).scalars().all()


def upload_result(inference_obj: Inference): 
    with SessionLocal() as session:
        session.add(inference_obj)
        session.commit()
        session.refresh(inference_obj)
        return inference_obj
