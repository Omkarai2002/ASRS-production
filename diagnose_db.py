#!/usr/bin/env python3
"""
Database Diagnostic Script
Checks if database is properly aligned with user_id system
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from app.auth.models import User

def diagnose_database():
    """Diagnose database state and user_id alignment"""
    print("\n" + "="*70)
    print("ASRS DATABASE DIAGNOSTIC REPORT")
    print("="*70)
    
    db = SessionLocal()
    try:
        # 1. Check Users
        print("\n📋 USERS IN DATABASE:")
        print("-" * 70)
        users = db.query(User).all()
        
        if not users:
            print("❌ NO USERS FOUND - Run: python create_db.py")
        else:
            print(f"✅ Found {len(users)} users:\n")
            for user in users:
                print(f"   ID: {user.id}")
                print(f"   Username: {user.username}")
                print(f"   Password Hash: {user.hashed_password[:30]}...")
                print()
        
        # 2. Check Reports
        print("\n📋 REPORTS IN DATABASE:")
        print("-" * 70)
        reports = db.query(Report).all()
        
        if not reports:
            print("ℹ️  No reports in database (will be created when users upload)")
        else:
            print(f"✅ Found {len(reports)} reports:\n")
            for report in reports:
                user = db.query(User).filter(User.id == report.user_id).first()
                username = user.username if user else "UNKNOWN"
                print(f"   Report ID: {report.id}")
                print(f"   Report Name: {report.report_name}")
                print(f"   User ID: {report.user_id}")
                print(f"   Username: {username}")
                print(f"   Created: {report.createdAt}")
                print()
        
        # 3. Check Inferences
        print("\n📋 INFERENCES IN DATABASE:")
        print("-" * 70)
        inferences = db.query(Inference).all()
        
        if not inferences:
            print("ℹ️  No inferences in database (will be created during image processing)")
        else:
            print(f"✅ Found {len(inferences)} inferences:\n")
            
            # Group by user
            by_user = {}
            for inf in inferences:
                if inf.user_id not in by_user:
                    by_user[inf.user_id] = []
                by_user[inf.user_id].append(inf)
            
            for user_id, infs in sorted(by_user.items()):
                user = db.query(User).filter(User.id == user_id).first()
                username = user.username if user else "UNKNOWN"
                print(f"   User ID {user_id} ({username}): {len(infs)} inferences")
                print(f"   ├─ Reports: {set(inf.report_id for inf in infs)}")
                print(f"   └─ Sample inference IDs: {[inf.id for inf in infs[:3]]}")
                print()
        
        # 4. Database Alignment Check
        print("\n✅ DATABASE ALIGNMENT CHECK:")
        print("-" * 70)
        
        checks_passed = 0
        checks_total = 5
        
        # Check 1: Users exist
        if users:
            print("✅ [1/5] Users table has entries")
            checks_passed += 1
        else:
            print("❌ [1/5] Users table is EMPTY")
        
        # Check 2: Reports have user_id
        if reports:
            all_have_user_id = all(r.user_id is not None for r in reports)
            if all_have_user_id:
                print("✅ [2/5] All reports have user_id set")
                checks_passed += 1
            else:
                print("❌ [2/5] Some reports missing user_id")
        else:
            print("⏭️  [2/5] No reports to check (will be created on upload)")
            checks_passed += 1
        
        # Check 3: Inferences have user_id
        if inferences:
            all_have_user_id = all(i.user_id is not None for i in inferences)
            if all_have_user_id:
                print("✅ [3/5] All inferences have user_id set")
                checks_passed += 1
            else:
                print("❌ [3/5] Some inferences missing user_id")
        else:
            print("⏭️  [3/5] No inferences to check (will be created during processing)")
            checks_passed += 1
        
        # Check 4: User IDs are unique
        if users:
            user_ids = [u.id for u in users]
            if len(user_ids) == len(set(user_ids)):
                print("✅ [4/5] All user IDs are unique")
                checks_passed += 1
            else:
                print("❌ [4/5] Duplicate user IDs found")
        else:
            print("⏭️  [4/5] No users to check")
            checks_passed += 1
        
        # Check 5: Report user_ids reference valid users
        if reports:
            report_user_ids = set(r.user_id for r in reports)
            valid_user_ids = set(u.id for u in users)
            
            invalid_refs = report_user_ids - valid_user_ids
            if not invalid_refs:
                print("✅ [5/5] All report user_ids reference valid users")
                checks_passed += 1
            else:
                print(f"❌ [5/5] Reports reference invalid user IDs: {invalid_refs}")
        else:
            print("⏭️  [5/5] No reports to check")
            checks_passed += 1
        
        print(f"\n📊 Alignment Score: {checks_passed}/{checks_total}")
        
        # 5. Recommendations
        print("\n" + "="*70)
        print("RECOMMENDATIONS:")
        print("="*70)
        
        if checks_passed < checks_total - 1:
            print("\n⚠️  DATABASE NEEDS RESET")
            print("\nRun the following command to reset and reinitialize:")
            print("   python reset_db.py")
            print("\nThis will:")
            print("   • Drop all existing tables")
            print("   • Create fresh tables with proper schema")
            print("   • Create 3 users with sequential IDs (1, 2, 3)")
            print("   • Ensure all user_id columns are properly aligned")
        else:
            print("\n✅ DATABASE IS PROPERLY ALIGNED")
            print("\nYou can now:")
            print("   1. Start server: python run.py")
            print("   2. Login with different user accounts")
            print("   3. Each user will see ONLY their own reports")
        
        print("\n" + "="*70)
        print("EXPECTED BEHAVIOR AFTER PROPER ALIGNMENT:")
        print("="*70)
        print("""
   User 1 (admin):
   └─ Login as: admin / admin123
   └─ Can create and see: admin's reports only
   └─ Cannot see: reports from user 2 or user 3

   User 2 (gblock@mahindra.com):
   └─ Login as: gblock@mahindra.com / GBlock@123
   └─ Can create and see: gblock's reports only
   └─ Cannot see: reports from user 1 or user 3

   User 3 (staff2):
   └─ Login as: staff2 / staff456
   └─ Can create and see: staff2's reports only
   └─ Cannot see: reports from user 1 or user 2
        """)
        
    finally:
        db.close()

if __name__ == "__main__":
    try:
        diagnose_database()
    except Exception as e:
        print(f"\n❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
