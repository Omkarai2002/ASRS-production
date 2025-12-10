# create_db.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.models import create_db_and_tables
from app.auth import create_user

create_db_and_tables()
# create a default user (username: admin, password: admin123) — change in real life
try:
    create_user("admin", "admin123")
    print("Created user admin/admin123")
except Exception as e:
    print("User may already exist:", e)
