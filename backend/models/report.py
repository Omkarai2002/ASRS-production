# backend/models/report.py
from sqlalchemy import Column, Integer, String, Date
from backend.database import Base

class Report(Base):
    __tablename__ = "reports"   # matches your RDS table name

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_name = Column(String(25), nullable=True)   # matches RDS
    createdAt = Column(Date, nullable=True)           # matches RDS
