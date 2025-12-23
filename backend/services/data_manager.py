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

def get_latest_unique_id(user_id: int):
    with SessionLocal() as session:
        # SELECT unique_id FROM `raw-data` WHERE user_id = %s ORDER BY id DESC LIMIT 1;
        stmt = select(RawData.unique_id).where(RawData.user_id == user_id).order_by(RawData.id.desc()).limit(1)
        result = session.execute(stmt).scalar_one_or_none()
        return result

def get_next_unique_id(user_id: int) -> str:
    unique_id = get_latest_unique_id(user_id)
    if not unique_id:
        return "@AA1111"

    # Logic provided by user:
    # if int(unique_id[3:]) != 9999: increment number
    # else: logic to increment prefix chars
    
    # Extract parts
    prefix = unique_id[:3]  # e.g. @AA
    number_part = unique_id[3:] # e.g. 1111
    
    try:
        number = int(number_part)
    except ValueError:
        # Fallback if existing ID doesn't match format
        return "@AA1111"

    if number != 9999:
        next_number = number + 1
        return f"{prefix}{next_number}"
    else:
        # Number is 9999, need to increment chars
        char1 = unique_id[1] # A
        char2 = unique_id[2] # A
        
        if char2 != 'Z':
            next_char2 = chr(ord(char2) + 1)
            return f"{unique_id[0]}{char1}{next_char2}1111"
        else:
            # char2 is Z
            next_char1 = chr(ord(char1) + 1)
            return f"{unique_id[0]}{next_char1}A1111"

def insert_raw_data(vin_no: str, date_val, user_id: int):
    unique_id = get_next_unique_id(user_id)
    with SessionLocal() as session:
        raw_data = RawData(
            unique_id=unique_id,
            vin_no=vin_no,
            createdAt=date_val,
            updatedAt=date_val,
            isDispatched=0,
            user_id=user_id
        )
        session.add(raw_data)
        session.commit()
        session.refresh(raw_data)
        return raw_data.unique_id
