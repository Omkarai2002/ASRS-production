# Complete Line Graph Fix - Step-by-Step Guide

## Problem Statement
Dashboard Activity Timeline showing "Reports Created: 0, Items Detected: 0" even after creating and processing reports.

## Root Causes Identified & Fixed

### Root Cause 1: Query Type Mismatch
- **Report.createdAt** is a `Date` column (not DateTime)
- Using `func.date()` on a Date column causes query mismatch
- **Fix**: Compare directly without `func.date()` for Date columns

### Root Cause 2: Missing Timestamps
- New reports weren't setting `createdAt` when inserted
- New inferences weren't setting `createdAt` when inserted
- **Fix**: Always set `createdAt` at time of insertion

## Changes Made

### 1. app/routers/dashboard.py
- Fixed daily statistics query to use `Report.createdAt == current_date` (not `func.date()`)
- Added detailed logging for debugging
- Lines: 100-145

### 2. backend/services/data_manager.py
- `create_report()` now sets `createdAt = date.today()`
- Added logging when reports are created
- `upload_result()` now logs when inferences are saved

### 3. backend/services/inferences.py
- Sets `createdAt = datetime.now()` when creating Inference objects
- Already had this, verified it's working

### 4. backend/helpers/db_queries.py
- Fixed all query patterns to match Date vs DateTime column types

## Testing Procedure

### Step 1: Reset Everything (Optional but Recommended)
```bash
# Stop the server (Ctrl+C)
# Delete old test data from database:
# DELETE FROM reports WHERE id > 0;
# DELETE FROM inferences WHERE id > 0;
```

### Step 2: Check Database Contents
```bash
cd /home/ostajanpure/Desktop/ASRS-prod
python debug_dashboard.py
```

**Expected output:**
```
DATABASE DIAGNOSTIC CHECK
========================
📊 RAW COUNTS (All users)
   Total Reports in DB: [some number]
   Total Inferences in DB: [some number]

📋 ALL REPORTS IN DATABASE
ID    User  Name                           CreatedAt       Type
[shows all reports with createdAt values]

📅 TODAY'S DATA (User ID = 1)
   Current date: 2025-12-25
   Reports today (user 1): [number]
   Inferences today (user 1): [number]
```

### Step 3: Start the Application
```bash
python run.py
```

**Check terminal output for:**
- `✅ Report created - ID: [X], Name: [Y], User: [Z], Date: [date]`
- `✅ Inference saved - ID: [X], Report: [Y], User: [Z], CreatedAt: [datetime]`

### Step 4: Create a Test Report
1. Login at http://localhost:8000/login
2. Go to Reports page
3. Create a report called "Test Dec 25"
4. Upload 2-3 test images
5. Click Submit

**What should happen in terminal:**
```
✅ Report created - ID: 5, Name: Test Dec 25, User: 1, Date: 2025-12-25
User 1: Processing image 1/3: test1.jpg
User 1: Processing image 2/3: test2.jpg
User 1: Processing image 3/3: test3.jpg
✅ Inference saved - ID: 101, Report: 5, User: 1, CreatedAt: 2025-12-25 14:23:45.123456
✅ Inference saved - ID: 102, Report: 5, User: 1, CreatedAt: 2025-12-25 14:23:46.234567
[etc...]
```

### Step 5: Verify Dashboard Updates
1. Click "Dashboard"
2. **Look for these changes:**
   - ✅ "Your Total Reports" increases by 1
   - ✅ "Your Items Detected" shows number of items processed
   - ✅ "Reports Today" shows 1
   - ✅ Activity Timeline shows spike on today's date

**Expected Dashboard:**
```
STATISTICS CARDS:
Your Total Reports:     5 (or higher)
Your Items Detected:    15+ (depends on items per image)
Reports Today:          1
System Status:          Active

ACTIVITY TIMELINE (Line Chart):
Date axis shows:   "Dec 21", "Dec 22", ..., "Dec 25"
Reports Created:   [Shows 1 on Dec 25, 0 on other days]
Items Detected:    [Shows items count on Dec 25, 0 on other days]
```

### Step 6: Debug Terminal Output
Run this while dashboard is open:
```bash
python debug_dashboard.py
```

Should now show:
- Reports today (user 1): 1
- Inferences today (user 1): 3 (or however many items were in images)
- Today's report listed in "ALL REPORTS"
- Today's inferences listed in "ALL INFERENCES"

## If Still Showing Zeros

### Diagnostic Steps

**1. Check report was created:**
```bash
python debug_dashboard.py
# Should show your report in "ALL REPORTS IN DATABASE" section
```

**2. Check inferences were saved:**
```bash
python debug_dashboard.py
# Should show your inferences in "ALL INFERENCES IN DATABASE" section
```

**3. Check timestamps are being set:**
```bash
python debug_dashboard.py
# CreatedAt column should show dates/times, NOT NULL
```

**4. Check app terminal for errors:**
```bash
# Look for lines with "❌" or "ERROR"
# Should see "✅ Report created..." and "✅ Inference saved..."
```

**5. Try a hard refresh of dashboard:**
```bash
# Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

**6. Check browser console for JS errors:**
```bash
# F12 → Console tab
# Look for red error messages
# Verify dailyData is being parsed correctly
```

## Additional Debug Command

To see exact data being sent to template:
1. In `app/routers/dashboard.py` after line 144, add:
   ```python
   print(f"DEBUG: daily_data = {daily_data}")
   print(f"DEBUG: total_reports = {total_reports}, items_detected = {items_detected}")
   ```
2. Restart server
3. Load dashboard
4. Check terminal for printed data

## Files You Can Check Manually

### To see raw report data:
```bash
mysql -u your_user -p
USE your_database;
SELECT * FROM reports ORDER BY createdAt DESC LIMIT 5;
SELECT * FROM inferences ORDER BY createdAt DESC LIMIT 10;
```

### To verify column types:
```bash
DESCRIBE reports;
DESCRIBE inferences;
```

Should show:
- `reports.createdAt` as `date` (or `datetime`)
- `inferences.createdAt` as `datetime`

## Summary of Fixes Applied

| Issue | Fix | File |
|-------|-----|------|
| Query fails on Date column | Use direct comparison instead of func.date() | dashboard.py, db_queries.py |
| Report created without date | Set createdAt = date.today() | data_manager.py |
| Inference without timestamp | Set createdAt = datetime.now() | inferences.py |
| Can't see what's in DB | Created debug_dashboard.py script | debug_dashboard.py |
| Can't debug queries | Added logging to dashboard route | dashboard.py |

Now the line graph should show real data immediately after creating a report!
