# backend/models/record.py
from sqlalchemy import Column, Integer, String
from backend.database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(100), unique=True, nullable=False)
    vin_no = Column(String(100), nullable=False)
    # Add more fields as per your requirements
