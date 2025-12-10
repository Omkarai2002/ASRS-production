# app/auth.py
from passlib.context import CryptContext
from typing import Optional
from sqlmodel import Session, select
from .models import engine, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(username: str) -> Optional[User]:
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

def create_user(username: str, password: str) -> User:
    hashed = get_password_hash(password)
    user = User(username=username, hashed_password=hashed)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
