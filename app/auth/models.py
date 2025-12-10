# app/models.py
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
