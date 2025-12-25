#!/usr/bin/env python
"""
ASRS Database Initialization Script
Initializes all required database tables and optionally seeds default data
"""

import sys
from backend.database import Base, engine, SessionLocal
from backend.models.user_settings import UserSettings
from backend.models.report import Report
from backend.models.inference import Inference
from sqlalchemy import text

def create_all_tables():
    """Create all database tables"""
    print("\n" + "="*60)
    print("INITIALIZING DATABASE TABLES")
    print("="*60)
    
    try:
        print("\n📊 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def verify_tables():
    """Verify that required tables exist"""
    print("\n" + "="*60)
    print("VERIFYING TABLES")
    print("="*60)
    
    required_tables = ['user_settings', 'reports', 'inferences']
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            existing_tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 Existing tables: {existing_tables}")
            
            all_exist = True
            for table_name in required_tables:
                if table_name in existing_tables:
                    print(f"✅ {table_name} table exists")
                else:
                    print(f"❌ {table_name} table NOT found")
                    all_exist = False
            
            return all_exist
    except Exception as e:
        print(f"⚠️ Could not verify tables: {str(e)}")
        return False

def create_default_settings():
    """Create default settings for existing users (if any)"""
    print("\n" + "="*60)
    print("INITIALIZING DEFAULT SETTINGS")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Get all users from SQLite
        from sqlite3 import connect as sqlite_connect
        sqlite_conn = sqlite_connect("app.db")
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT id FROM user")
        users = cursor.fetchall()
        sqlite_conn.close()
        
        created_count = 0
        for user_id, in users:
            # Check if settings already exist
            existing = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if not existing:
                # Create default settings
                settings = UserSettings(
                    user_id=user_id,
                    images_per_row=8,
                    level_prefix="L",
                    image_size="medium",
                    show_image_info=True,
                    show_level_info=True
                )
                db.add(settings)
                created_count += 1
        
        db.commit()
        print(f"✅ Created default settings for {created_count} user(s)")
        return True
    except Exception as e:
        print(f"⚠️ Could not create default settings: {str(e)}")
        print("   (This is OK - settings will be created on first visit to /settings)")
        return True
    finally:
        db.close()

def main():
    """Main initialization routine"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  ASRS DATABASE INITIALIZATION".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60 + "\n")
    
    # Step 1: Create tables
    if not create_all_tables():
        print("\n❌ Failed to create tables. Exiting.")
        sys.exit(1)
    
    # Step 2: Verify tables
    if not verify_tables():
        print("\n⚠️ Some tables may be missing, but attempting to continue...")
    
    # Step 3: Create default settings
    create_default_settings()
    
    # Final status
    print("\n" + "="*60)
    print("INITIALIZATION STATUS")
    print("="*60)
    print("\n✅ DATABASE INITIALIZATION COMPLETE!\n")
    print("Next steps:")
    print("  1. Start the server: python run.py")
    print("  2. Navigate to: http://localhost:8000/dashboard")
    print("  3. Visit /settings to customize visualization preferences")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
