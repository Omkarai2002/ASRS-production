# create_db.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.auth.models import create_db_and_tables
from app.auth.auth import create_user

create_db_and_tables()

# Create pre-assigned admin/staff users with fixed credentials
users = [
    {"username": "admin", "password": "admin123"},
    {"username": "gblock@mahindra.com", "password": "GBlock@123"},
    {"username": "staff2", "password": "staff456"},
    # Add more users as needed:
    # {"username": "user_name", "password": "password"},
]

for user in users:
    try:
        created_user = create_user(user["username"], user["password"])
        print(f"✅ Created user: {user['username']} (ID: {created_user.id})")
    except Exception as e:
        print(f"⚠️  User '{user['username']}' may already exist: {e}")
