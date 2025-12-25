# Line Graph Data Fix - Testing Guide

## Problem Summary
The Activity Timeline (line graph) on the Dashboard was showing all zeros for "Reports Created" and "Items Detected" even after creating reports and uploading images.

## Root Cause Identified
The issue was in `/app/routers/dashboard.py` when querying daily statistics:
- `Report.createdAt` is defined as a `Date` type (not `DateTime`)
- The query was using `func.date(Report.createdAt) == current_date` on a Date column
- This redundant function call caused the query to return no matches, resulting in zeros

## Solution Applied
Updated the daily statistics query in `dashboard.py`:
- For `Report`: Compare directly without `func.date()` since it's already a Date column
  ```python
  Report.createdAt == current_date  # Correct for Date column
  ```
- For `Inference`: Use `func.date()` since it's a DateTime column
  ```python
  func.date(Inference.createdAt) == current_date  # Correct for DateTime column
  ```

## Files Modified
1. **app/routers/dashboard.py** (Lines 100-125)
   - Fixed Report query to use direct comparison
   - Kept Inference query with func.date()
   
2. **backend/services/data_manager.py** (Previously updated)
   - Now sets `createdAt = date.today()` when creating reports

3. **backend/services/inferences.py** (Previously updated)
   - Now sets `createdAt = datetime.now()` when saving inferences

## Testing Steps

### Step 1: Start the Application
```bash
python run.py
```
Or if using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

### Step 2: Login
- Navigate to http://localhost:8000/login
- Use your test credentials

### Step 3: Create a New Report
- Go to "Reports" → "Create Report"
- Upload 2-3 test images
- Name the report something like "Test Report Dec 25"
- Submit the form

### Step 4: Wait for Processing
- Wait 10-30 seconds for the background task to process images
- You should see success message

### Step 5: Verify Dashboard
- Click on "Dashboard"
- You should now see:
  - **Total Reports**: Should increase by 1
  - **Items Detected**: Should show the number of images processed
  - **Reports Today**: Should show 1 (if created today)
  - **Activity Timeline**: The line graph should show a spike on today's date with:
    - "Reports Created" = 1
    - "Items Detected" = number of items processed

### Step 6: Test Filtering
- Use the date filters to test:
  - "From Date" = today
  - "To Date" = today
  - Click "Apply Filters"
- Stats should match the report you created

## Expected Behavior After Fix
✅ Reports created appear immediately in total count  
✅ Items detected appear immediately after processing  
✅ Line chart shows correct daily counts  
✅ Date filters work correctly  
✅ All exclusion statistics update properly  

## Database Query Debugging
If you want to verify the database directly, you can run:
```sql
-- Check reports created today (replace with your user_id)
SELECT COUNT(*) FROM reports WHERE user_id = 1 AND DATE(createdAt) = CURDATE();

-- Check inferences created today
SELECT COUNT(*) FROM inferences WHERE user_id = 1 AND DATE(createdAt) = CURDATE();
```

## Troubleshooting

### Still showing zeros?
1. Check browser console (F12 → Console) for JavaScript errors
2. Check application terminal for Python errors
3. Verify `createdAt` is being set:
   ```sql
   SELECT id, report_name, createdAt FROM reports ORDER BY id DESC LIMIT 5;
   ```

### Chart not updating after refresh?
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear browser cache
- Check if JavaScript console shows parse errors with the JSON data

### Very slow query?
- Add database indexes (optional, for production):
  ```sql
  CREATE INDEX idx_reports_user_date ON reports(user_id, createdAt);
  CREATE INDEX idx_inferences_user_date ON inferences(user_id, createdAt);
  ```

## Next Steps (Optional Improvements)
1. **Auto-refresh dashboard**: Add polling to update chart every 30 seconds without page reload
2. **DateTime migration**: Convert `reports.createdAt` from Date to DateTime for more precision
3. **Database defaults**: Set MySQL column defaults to `CURRENT_TIMESTAMP` for robustness
4. **Caching**: Cache daily stats for frequently accessed time ranges
