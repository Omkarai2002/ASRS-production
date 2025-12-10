from app.auth import authenticate_user
from app.auth.models import engine, User
from sqlmodel import Session, select

print("Testing login...")

user = authenticate_user("admin", "admin123")

print("Result:", user)
