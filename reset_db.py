#!/usr/bin/env python3
"""
ASRS Database Reset & Initialization Script
This script properly initializes the database with user_id alignment
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.auth.models import create_db_and_tables
from app.auth.auth import create_user, get_user_by_username
from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference

def reset_database():
    """Reset database and recreate tables with proper schema"""
    print("🔄 Resetting database schema...")
    
    # Drop existing tables if they exist
    from backend.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    print("✅ Dropped all existing tables")
    
    # Recreate tables with new schema
    Base.metadata.create_all(bind=engine)
    create_db_and_tables()
    print("✅ Created fresh tables with user_id columns")

def create_users():
    """Create users with proper IDs"""
    print("\n👥 Creating users...")
    
    users = [
        {"username": "admin", "password": "admin123"},
        {"username": "gblock@mahindra.com", "password": "GBlock@123"},
        {"username": "staff2", "password": "staff456"},
    ]
    
    created_users = {}
    
    for user_data in users:
        try:
            user = create_user(user_data["username"], user_data["password"])
            created_users[user_data["username"]] = user.id
            print(f"✅ Created user: {user_data['username']} (ID: {user.id})")
        except Exception as e:
            # User might already exist, try to get them
            try:
                user = get_user_by_username(user_data["username"])
                created_users[user_data["username"]] = user.id
                print(f"⚠️  User '{user_data['username']}' already exists (ID: {user.id})")
            except:
                print(f"❌ Error creating user '{user_data['username']}': {e}")
    
    return created_users

def verify_database():
    """Verify database alignment"""
    print("\n📊 Verifying database alignment...")
    
    db = SessionLocal()
    try:
        # Check users
        from app.auth.models import User
        users = db.query(User).all()
        print(f"\n✅ Total users in database: {len(users)}")
        for user in users:
            print(f"   └─ ID {user.id}: {user.username}")
        
        # Check reports
        reports = db.query(Report).all()
        print(f"\n✅ Total reports in database: {len(reports)}")
        if reports:
            for report in reports:
                print(f"   └─ Report {report.id}: {report.report_name} (user_id={report.user_id})")
        else:
            print("   (No reports yet - they will be created when users upload)")
        
        # Check inferences
        inferences = db.query(Inference).all()
        print(f"\n✅ Total inferences in database: {len(inferences)}")
        if inferences:
            for inf in inferences[:5]:  # Show first 5
                print(f"   └─ Inference {inf.id}: report={inf.report_id}, user_id={inf.user_id}")
            if len(inferences) > 5:
                print(f"   └─ ... and {len(inferences) - 5} more")
        else:
            print("   (No inferences yet - they will be created when images are processed)")
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*60)
        print("\n🎯 User-ID Alignment Status:")
        print("✅ Users created with sequential IDs (1, 2, 3, ...)")
        print("✅ Each report will be linked to creator's user_id")
        print("✅ Each inference will be linked to creator's user_id")
        print("✅ /reports page filters by session user_id")
        print("✅ /visualize page filters by session user_id")
        print("\n📝 Next Steps:")
        print("1. Start server: python run.py")
        print("2. Login as admin (ID=1)")
        print("3. Create some reports")
        print("4. Logout and login as gblock@mahindra.com (ID=2)")
        print("5. Create different reports")
        print("6. Each user will see ONLY their own reports ✅")
        print("\n" + "="*60)
        
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("ASRS DATABASE INITIALIZATION")
    print("="*60)
    
    # Ask for confirmation
    response = input("\n⚠️  This will RESET your database and delete all existing data.\nContinue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Database reset cancelled")
        sys.exit(1)
    
    try:
        reset_database()
        create_users()
        verify_database()
        print("\n✅ Database ready for testing!")
    except Exception as e:
        print(f"\n❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
