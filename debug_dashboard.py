#!/usr/bin/env python3
"""
Diagnostic script to check actual database contents
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, timedelta
from backend.database import SessionLocal
from backend.models.report import Report
from backend.models.inference import Inference
from sqlalchemy import func, text

def check_database():
    """Check raw database contents"""
    db = SessionLocal()
    try:
        print(f"\n{'='*70}")
        print(f"DATABASE DIAGNOSTIC CHECK")
        print(f"{'='*70}\n")
        
        # Raw count
        all_reports = db.query(Report).all()
        all_inferences = db.query(Inference).all()
        
        print(f"📊 RAW COUNTS (All users)")
        print(f"   Total Reports in DB: {len(all_reports)}")
        print(f"   Total Inferences in DB: {len(all_inferences)}\n")
        
        # Show all reports
        if all_reports:
            print(f"📋 ALL REPORTS IN DATABASE")
            print(f"{'ID':<5} {'User':<6} {'Name':<30} {'CreatedAt':<15} {'Type':<10}")
            print(f"{'-'*66}")
            for r in all_reports:
                print(f"{r.id:<5} {str(r.user_id):<6} {(r.report_name or 'N/A'):<30} {str(r.createdAt):<15} {type(r.createdAt).__name__:<10}")
        else:
            print("   ❌ NO REPORTS FOUND IN DATABASE")
        
        # Show all inferences
        if all_inferences:
            print(f"\n� ALL INFERENCES IN DATABASE (First 20)")
            print(f"{'ID':<5} {'User':<6} {'Report':<8} {'VIN':<15} {'CreatedAt':<20} {'Type':<10}")
            print(f"{'-'*74}")
            for inf in all_inferences[:20]:
                vin = (inf.vin_no or "N/A")[:12]
                created_str = str(inf.createdAt)[:19] if inf.createdAt else "NULL"
                print(f"{inf.id:<5} {str(inf.user_id):<6} {str(inf.report_id):<8} {vin:<15} {created_str:<20} {type(inf.createdAt).__name__:<10}")
        else:
            print("   ❌ NO INFERENCES FOUND IN DATABASE")
        
        # Check today's data for user 1
        print(f"\n📅 TODAY'S DATA (User ID = 1)")
        today = date.today()
        print(f"   Current date: {today}\n")
        
        user_1_reports_today = db.query(Report).filter(
            Report.user_id == 1,
            Report.createdAt == today
        ).all()
        
        user_1_inferences_today = db.query(Inference).filter(
            Inference.user_id == 1,
            func.date(Inference.createdAt) == today
        ).all()
        
        print(f"   Reports today (user 1): {len(user_1_reports_today)}")
        print(f"   Inferences today (user 1): {len(user_1_inferences_today)}")
        
        if user_1_reports_today:
            for r in user_1_reports_today:
                print(f"      - Report {r.id}: {r.report_name} (createdAt: {r.createdAt})")
        
        if user_1_inferences_today:
            for inf in user_1_inferences_today[:5]:
                print(f"      - Inference {inf.id}: VIN={inf.vin_no}, User={inf.user_id}, CreatedAt={inf.createdAt}")
        
        # Check table structure
        print(f"\n� TABLE SCHEMA CHECK")
        try:
            result = db.execute(text("DESCRIBE reports")).fetchall()
            print(f"   Report.createdAt column info:")
            for row in result:
                if 'createdAt' in str(row[0]):
                    print(f"      {row}")
        except:
            pass
        
        try:
            result = db.execute(text("DESCRIBE inferences")).fetchall()
            print(f"   Inference.createdAt column info:")
            for row in result:
                if 'createdAt' in str(row[0]):
                    print(f"      {row}")
        except:
            pass
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
