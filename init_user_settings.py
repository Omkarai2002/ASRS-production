"""
Create user_settings table in MySQL database
Run this script once to initialize the table
"""

from backend.database import Base, engine
from backend.models.user_settings import UserSettings
from sqlalchemy import text

def create_tables():
    """Create all tables defined in models"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Verify table was created
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES LIKE 'user_settings'"))
            if result.fetchone():
                print("✅ user_settings table verified in database")
            else:
                print("❌ user_settings table NOT found")
    except Exception as verify_error:
        print(f"⚠️ Could not verify table (this is OK): {verify_error}")
        print("✅ Table creation command executed successfully")

if __name__ == "__main__":
    try:
        create_tables()
        print("\n✅ Database initialization complete!")
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        import traceback
        traceback.print_exc()
