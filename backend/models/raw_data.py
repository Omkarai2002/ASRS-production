# backend/models/record.py
from sqlalchemy import Column, Date, Integer, String
from backend.database import Base

class RawData(Base):
    __tablename__ = "raw-data"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(100), unique=True, nullable=False)
    vin_no = Column(String(100), nullable=False)
    createdAt = Column(Date, nullable=True) 
    updatedAt = Column(Date, nullable=True)
    isDispatched = Column(String(100), nullable=True)
    user_id = Column(Integer, nullable=True)
    # Add more fields as per your requirements
