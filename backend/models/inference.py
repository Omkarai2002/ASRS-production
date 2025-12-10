# backend/models/inference.py
from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database import Base

class Inference(Base):
    __tablename__ = "inferences"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, nullable=False)
    image_name = Column(String(200), nullable=False)
    unique_id = Column(String(100), nullable=True)
    quantity = Column(Integer, default=1)
    vin_no = Column(String(50), nullable=True)
    exclusion = Column(String(100), default="")
    s3_url = Column(String(500), nullable=True)
