#!/usr/bin/env python3
"""
View all users in the database with user_id
"""

from backend.database import SessionLocal
from app.auth.models import User

def view_users():
    db = SessionLocal()
    try:
        users = db.query().order_by(User.id).all()

        if not users:
            print("❌ No users found in the database.")
            return

        print("\n" + "=" * 50)
        print("👥 USERS IN DATABASE")
        print("=" * 50)

        for user in users:
            print(f"ID: {user.id:<5} | Username: {user.username}")

        print("=" * 50)
        print(f"Total users: {len(users)}\n")

    finally:
        db.close()

if __name__ == "__main__":
    view_users()
