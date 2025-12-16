from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.database import Base

class Inference(Base):
    __tablename__ = "inferences"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(7), nullable=True)  # char(7)
    image_name = Column(String(255), nullable=True)
    vin_no = Column(String(25), nullable=True)
    quantity = Column(Integer, nullable=True)
    exclusion = Column(String(255), nullable=True)

    createdAt = Column(DateTime, nullable=True)
    updatedAt = Column(DateTime, nullable=True)

    report_id = Column(Integer, nullable=True)
    is_non_confirmity = Column(Boolean, default=False)

    s3_obj_url = Column(String(255), nullable=True)  # correct name
