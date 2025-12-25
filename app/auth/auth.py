# app/auth.py
from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.database import SessionLocal
from backend.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(email: str) -> Optional[User]:
    with SessionLocal() as session:
        statement = select(User).where(User.email == email)
        result = session.execute(statement)
        return result.scalars().first()

def create_user(email: str, password: str) -> User:
    hashed = get_password_hash(password)
    user = User(email=email, password=hashed)
    with SessionLocal() as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def authenticate_user(email: str, password: str) -> Optional[User]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
