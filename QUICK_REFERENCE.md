# ASRS Code Flow - Quick Reference Guide

## 📍 Where to Look for Specific Features

### 🔐 **Authentication & User Sessions**
- **Login page:** `app/templates/login.html`
- **Signup page:** `app/templates/signup.html`
- **Auth routes:** `app/routers/auth_routes.py`
- **Auth functions:** `app/auth/auth.py`
- **User model:** `app/auth/models.py`
- **Session management:** `app/main.py` (SessionMiddleware)

### 📋 **Reports Management**
- **Reports page UI:** `app/templates/reports.html`
- **Reports routes:** `app/routers/reports.py`
- **Report creation:** `app/routers/reports.py` → `POST /reports/create`
- **Database model:** `backend/models/report.py`
- **CRUD operations:** `backend/services/data_manager.py`

### 📤 **File Upload & Processing**
- **Upload page UI:** `app/templates/upload.html`
- **Upload routes:** `app/routers/upload.py`
- **Background processing:** `backend/services/inferences.py` → `get_inferences()`
- **Image cleanup:** `backend/services/inferences.py` → finally block
- **Database storage:** `/uploads/` and `/uploaded_reports/`

### 🔍 **Image Processing Pipeline**
1. **OCR (Text Recognition):** `backend/services/google_ocr.py`
2. **Parse Results:** `backend/services/annotations_parser.py`
3. **Vehicle Detection:** `backend/services/detection.py`
4. **Build Results:** `backend/services/json_result.py`
5. **Upload to S3:** `backend/services/s3_operator.py`
6. **Save to Database:** `backend/services/data_manager.py`

### 👁️ **Report Visualization & Export**
- **Visualize page UI:** `app/templates/visualize.html`
- **Visualize routes:** `app/routers/visualize.py`
- **Auto-load report:** `app/routers/visualize.py` → `GET /visualize?report={id}`
- **JSON API:** `app/routers/visualize.py` → `GET /api/report/{id}/details`
- **Excel export:** `app/routers/visualize.py` → `export_report_excel()`
- **Excel generation:** Uses `openpyxl` library

### 📊 **Dashboard & Statistics**
- **Dashboard page:** `app/templates/dashboard.html`
- **Dashboard routes:** `app/routers/dashboard.py`
- **Statistics queries:** `app/routers/dashboard.py`
- **Chart data:** Database queries in dashboard route

### 🎯 **QR Code Generation**
- **QR page:** `app/templates/qr_generation.html`
- **QR routes:** `app/routers/qr_generation.py`
- **QR service:** `backend/services/qr_generation.py`

### 🎨 **Frontend Styling**
- **Base layout:** `app/templates/base.html`
- **Styles:** `app/static/css/style.css`
- **JavaScript:** `app/static/js/script.js`
- **Design system:** CSS variables in `base.html`

---

## 📊 Database Models Relationships

### Report Model
```python
backend/models/report.py

Report:
  ├─ id (Primary Key)
  ├─ report_name
  ├─ createdAt
  └─ inferences (Relationship → Many Inferences)
```

### Inference Model
```python
backend/models/inference.py

Inference:
  ├─ id (Primary Key)
  ├─ report_id (Foreign Key → Report)
  ├─ image_name
  ├─ unique_id
  ├─ vin_no
  ├─ quantity
  ├─ exclusion
  ├─ is_non_conformity
  ├─ s3_obj_url (← Image location on AWS S3)
  └─ createdAt
```

---

## 🔄 Key Request-Response Flows

### Flow 1: User Creates Report
```
User fills form on /reports
    ↓
POST /reports/create (report_name, files[])
    ↓
reports.py: Validates input
    ↓
data_manager.py: Creates Report in DB
    ↓
Save files to /uploads/{name}/
    ↓
background_tasks.add_task(get_inferences, ...)
    ↓
Respond with redirect to /reports
    ↓
User sees success message
    ↓
[Background] inferences.py processes images:
  - google_ocr.py: Extract text
  - annotations_parser.py: Parse IDs
  - detection.py: Detect objects
  - s3_operator.py: Upload to S3
  - data_manager.py: Save results
  - shutil: Delete temp folder
```

### Flow 2: User Views Report Details
```
User clicks "View Details" on report card
    ↓
Navigate to /visualize?report=5
    ↓
visualize.py: Renders page with selected_report data
    ↓
JavaScript: Detects ?report=5 parameter
    ↓
Auto-clicks report in sidebar
    ↓
loadReport(5) JavaScript function:
  - Fetches /api/report/5/details
  - Receives JSON with all inferences
  - Renders HTML with images & details
    ↓
User sees full report details
```

### Flow 3: User Downloads Excel
```
User clicks "Download Excel" button
    ↓
GET /api/report/5/export/excel
    ↓
visualize.py: export_report_excel():
  - Query report & inferences
  - Create openpyxl Workbook
  - Add formatted headers
  - Add data rows with hyperlinks
  - Return as XLSX file
    ↓
Browser downloads: Report_5_ReportName.xlsx
    ↓
User opens in Excel with all data
```

---

## 🛠️ Important Code Patterns

### Pattern 1: Database Session Management
```python
# In any service or route
from backend.database import SessionLocal

db = SessionLocal()
try:
    # Query or modify database
    report = db.query(Report).filter(...).first()
    db.add(new_object)
    db.commit()
finally:
    db.close()
```

### Pattern 2: Background Task Processing
```python
# In route handler
from fastapi import BackgroundTasks

async def create_report(background_tasks: BackgroundTasks):
    # Quick response
    background_tasks.add_task(long_running_function, args)
    return {"status": "processing"}
    # Function runs asynchronously
```

### Pattern 3: Template with Auto-Selection
```html
<!-- In visualize.html -->
<div class="report-item" 
     data-report-id="5"
     onclick="loadReport(5, this)">
</div>

<script>
// Auto-select if passed via URL
const reportId = new URLSearchParams(window.location.search).get('report');
if (reportId) {
    document.querySelector(`[data-report-id="${reportId}"]`).click();
}
</script>
```

---

## 🚀 Testing Each Feature

### Test 1: Create Report
1. Go to http://localhost:8000/reports
2. Fill "Report Name" field
3. Upload images (drag-drop or click)
4. Click "Create Report"
5. ✅ Should see success message
6. ✅ Report appears in list (latest first)

### Test 2: View Report Details
1. On /reports page, click "View Details" on any report
2. ✅ Should navigate to /visualize?report={id}
3. ✅ Report should auto-load (don't need to search)
4. ✅ See all inferences with images from S3

### Test 3: Download Excel
1. In /visualize page, open any report
2. Click "Download Excel" button
3. ✅ Excel file downloads: Report_{id}_{name}.xlsx
4. ✅ Open in Excel, see:
   - Report info at top
   - Formatted table with all inferences
   - "Download" links (clickable S3 URLs)

### Test 4: Date Range Filtering
1. On /reports or /visualize page
2. Set "From Date" and "To Date"
3. ✅ Reports list filters to show only matching dates
4. Click "Reset" button
5. ✅ All reports reappear

### Test 5: Upload Cleanup
1. Upload report with multiple images
2. Processing starts in background
3. Check `/uploads/` folder
4. ✅ While processing: folder exists
5. ✅ After processing: folder deleted automatically

---

## 📁 File Organization Logic

```
Frontend (User-facing)
├─ app/templates/*.html  (What users see)
├─ app/static/css/*.css  (Styling)
└─ app/static/js/*.js    (Interactivity)

Routes (Request handlers)
├─ app/routers/*.py      (HTTP endpoints)
└─ app/auth/             (Auth logic)

Data Layer
├─ backend/database.py   (DB connection)
├─ backend/models/       (Table schemas)
└─ backend/services/     (Business logic)

Configuration
├─ requirements.txt      (Dependencies)
├─ .env                  (Secrets)
└─ app.db                (SQLite database)

Utils
├─ run.py                (Start server)
├─ app/main.py           (App setup)
└─ create_db.py          (Init database)
```

---

## 🔑 Key Files to Understand First

### For Frontend Developers
1. `app/templates/base.html` - Layout & structure
2. `app/static/css/style.css` - All styling
3. `app/templates/reports.html` - Reports UI
4. `app/templates/visualize.html` - Visualization UI

### For Backend Developers
1. `run.py` - Entry point
2. `app/main.py` - App configuration
3. `backend/database.py` - DB setup
4. `app/routers/reports.py` - Example route
5. `backend/services/inferences.py` - Processing logic

### For Full-Stack Understanding
1. Start: `CODE_FLOW_DOCUMENTATION.md` (this file explains it all)
2. Follow: `run.py` → `app/main.py` → any route
3. Trace: Database models & services
4. View: Templates to see how data is displayed

---

## 🎯 Common Tasks & Where to Find Code

| Task | File(s) |
|------|---------|
| Add new page | Create `app/templates/new.html`, add route in `app/routers/new.py` |
| Change colors | Edit `app/static/css/style.css` or CSS vars in `base.html` |
| Add database field | Edit model in `backend/models/`, run migration |
| Create new API endpoint | Add `@router.get/post()` in appropriate `app/routers/file.py` |
| Add business logic | Create function in `backend/services/new.py` |
| Schedule task | Use `background_tasks.add_task()` in routes |
| Generate report | Call/modify `app/routers/visualize.py` export functions |
| Fix authentication | Check `app/auth/auth.py` and `session` middleware |

---

## 🐛 Debugging Tips

### Issue: Page shows wrong data
- Check: Is database query correct? (`backend/models/`)
- Check: Is data passed to template? (route in `app/routers/`)
- Check: Is template displaying correctly? (`app/templates/`)

### Issue: Background processing fails
- Check: Are all required services imported?
- Check: Are external API credentials valid? (`.env` file)
- Check: Database session being closed? (finally block)

### Issue: Images not showing
- Check: S3 URLs valid? (`backend/services/s3_operator.py`)
- Check: AWS credentials working? (`.env` file)
- Check: Image saved to S3? (logs in inferences.py)

### Issue: Excel export empty
- Check: Are inferences in database? (backend/models/inference.py)
- Check: Is query correct? (`app/routers/visualize.py`)
- Check: Is openpyxl installed? (`pip install openpyxl`)

---

## 📞 Quick Help

**Q: Where is my uploaded file saved?**  
A: While processing: `/uploads/{report_name}/` → Gets deleted after processing  
Processed images: AWS S3 bucket (URL stored in Inference.s3_obj_url)

**Q: How long does image processing take?**  
A: Depends on image size and detection model. Happens in background, doesn't block UI.

**Q: Can I re-download the same Excel file?**  
A: Yes! Excel is generated on-demand from database data using `/api/report/{id}/export/excel`

**Q: How do I add a new field to the report?**  
A: 
1. Add field to `backend/models/report.py`
2. Update database (migration or recreation)
3. Update route to save this field
4. Update template to display it

**Q: How do I integrate a new external API?**  
A: 
1. Create new file in `backend/services/new_service.py`
2. Write functions to call the API
3. Import in relevant routes (`app/routers/`)
4. Use in appropriate place (background task or sync request)

---

## ✅ Code Quality Checklist

When adding new features:
- [ ] Database model in `backend/models/`
- [ ] Service logic in `backend/services/`
- [ ] Routes in `app/routers/`
- [ ] Template in `app/templates/`
- [ ] Styling in `app/static/css/style.css`
- [ ] Handle errors with try/except
- [ ] Close database sessions with finally
- [ ] Long operations in background tasks
- [ ] Add comments for complex logic
- [ ] Test all user flows

---

## 📚 Learning Path

1. **Beginner:** Read this guide + CODE_FLOW_DOCUMENTATION.md
2. **Intermediate:** Follow request from route → service → database
3. **Advanced:** Understand async/background processing, S3 integration
4. **Expert:** Optimize queries, add caching, improve performance

---

**Version:** 1.0  
**Created:** December 14, 2025  
**For:** ASRS Development Team
