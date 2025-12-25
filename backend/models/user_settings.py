from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.database import Base
from datetime import datetime

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)  # Link to user
    
    # Visualization settings
    images_per_row = Column(Integer, default=8)  # Number of images in each row
    level_prefix = Column(String(50), default="L")  # Prefix for level naming (e.g., "L", "Level", "Storage")
    
    # Additional settings for future expansion
    image_size = Column(String(50), default="medium")  # small, medium, large
    show_image_info = Column(Boolean, default=True)  # Show image metadata
    show_level_info = Column(Boolean, default=True)  # Show level information
    
    # Timestamps
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, images_per_row={self.images_per_row}, level_prefix={self.level_prefix})>"
