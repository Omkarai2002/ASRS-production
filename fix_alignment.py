#!/usr/bin/env python3
"""
Fix Database Alignment - Align Reports/Inferences with Users in MySQL
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.database import SessionLocal, Base, engine
from backend.models.report import Report
from backend.models.inference import Inference
from app.auth.models import User as AuthUser

def fix_database_alignment():
    """Fix database alignment between SQLite auth and MySQL backend"""
    print("\n" + "="*70)
    print("ASRS DATABASE ALIGNMENT FIX")
    print("="*70)
    
    # Step 1: Check SQLite users
    print("\n📋 Step 1: Checking SQLite authentication database...")
    try:
        from app.auth.models import engine as auth_engine
        from app.auth.models import User
        from sqlmodel import Session as SQLSession
        
        with SQLSession(auth_engine) as session:
            users = session.query(User).all()
            print(f"✅ Found {len(users)} users in app.db (SQLite):")
            for user in users:
                print(f"   └─ ID: {user.id}, Username: {user.username}")
            auth_users = {u.id: u.username for u in users}
    except Exception as e:
        print(f"❌ Error reading auth database: {e}")
        return
    
    if not auth_users:
        print("❌ No users found in authentication database")
        print("Run: python create_db.py")
        return
    
    # Step 2: Check MySQL reports
    print("\n📋 Step 2: Checking MySQL reports...")
    db = SessionLocal()
    try:
        reports = db.query(Report).all()
        print(f"✅ Found {len(reports)} reports in MySQL:")
        
        if reports:
            for report in reports:
                print(f"   └─ ID: {report.id}, Name: {report.report_name}, user_id: {report.user_id}")
        else:
            print("   (No reports in database yet)")
    except Exception as e:
        print(f"❌ Error reading reports: {e}")
        db.close()
        return
    
    # Step 3: Fix report user_id alignment
    print("\n📋 Step 3: Fixing report alignment...")
    
    if reports:
        reports_without_user = [r for r in reports if r.user_id is None]
        if reports_without_user:
            print(f"⚠️  Found {len(reports_without_user)} reports without user_id")
            
            # Ask which user to assign them to
            print("\n👥 Available users:")
            for uid, uname in sorted(auth_users.items()):
                print(f"   {uid}: {uname}")
            
            try:
                default_user_id = min(auth_users.keys())
                response = input(f"\nAssign orphaned reports to user ID (default: {default_user_id}): ").strip()
                user_id_to_assign = int(response) if response else default_user_id
                
                if user_id_to_assign not in auth_users:
                    print(f"❌ User ID {user_id_to_assign} not found")
                    db.close()
                    return
                
                for report in reports_without_user:
                    report.user_id = user_id_to_assign
                
                db.commit()
                print(f"✅ Assigned {len(reports_without_user)} reports to user ID {user_id_to_assign}")
            except ValueError:
                print("❌ Invalid user ID")
                db.close()
                return
        else:
            print("✅ All reports have user_id set")
    
    # Step 4: Fix inference user_id alignment
    print("\n📋 Step 4: Fixing inference alignment...")
    try:
        inferences = db.query(Inference).all()
        print(f"✅ Found {len(inferences)} inferences in MySQL:")
        
        if inferences:
            inferences_without_user = [i for i in inferences if i.user_id is None]
            if inferences_without_user:
                print(f"⚠️  Found {len(inferences_without_user)} inferences without user_id")
                
                # Try to get user_id from associated report
                fixed_count = 0
                for inf in inferences_without_user:
                    report = db.query(Report).filter(Report.id == inf.report_id).first()
                    if report and report.user_id:
                        inf.user_id = report.user_id
                        fixed_count += 1
                
                if fixed_count < len(inferences_without_user):
                    print(f"⚠️  Could only fix {fixed_count} inferences from reports")
                    
                    # Ask for default user
                    default_user_id = min(auth_users.keys())
                    response = input(f"Assign remaining to user ID (default: {default_user_id}): ").strip()
                    user_id_to_assign = int(response) if response else default_user_id
                    
                    for inf in inferences_without_user:
                        if inf.user_id is None:
                            inf.user_id = user_id_to_assign
                    
                    db.commit()
                    print(f"✅ Fixed all {len(inferences_without_user)} inferences")
                else:
                    db.commit()
                    print(f"✅ Fixed {fixed_count} inferences from report owners")
            else:
                print("✅ All inferences have user_id set")
    except Exception as e:
        print(f"❌ Error fixing inferences: {e}")
        db.close()
        return
    
    db.close()
    
    # Step 5: Verification
    print("\n📋 Step 5: Verifying alignment...")
    db = SessionLocal()
    try:
        reports_verified = db.query(Report).all()
        inferences_verified = db.query(Inference).all()
        
        all_reports_good = all(r.user_id is not None for r in reports_verified)
        all_inferences_good = all(i.user_id is not None for i in inferences_verified)
        
        if all_reports_good and all_inferences_good:
            print("✅ All data properly aligned with user_id system")
        else:
            if not all_reports_good:
                print(f"❌ Some reports still missing user_id")
            if not all_inferences_good:
                print(f"❌ Some inferences still missing user_id")
    finally:
        db.close()
    
    print("\n" + "="*70)
    print("✅ DATABASE ALIGNMENT COMPLETE")
    print("="*70)
    print("""
Next steps:
1. Start your server: python run.py
2. Login as each user and verify they see ONLY their reports
3. Create new reports as different users
4. Each user should see ONLY their own data

User Credentials:
""")
    for uid, uname in sorted(auth_users.items()):
        print(f"  • ID {uid}: {uname}")
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        fix_database_alignment()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
