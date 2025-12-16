# ASRS Architecture - Visual Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASRS APPLICATION                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      PRESENTATION LAYER (Frontend)                   │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                       │   │
│  │   Browser (HTML5/CSS3/JavaScript)                                  │   │
│  │   ├─ app/templates/base.html (Layout)                             │   │
│  │   ├─ app/templates/login.html                                     │   │
│  │   ├─ app/templates/dashboard.html                                 │   │
│  │   ├─ app/templates/reports.html                                   │   │
│  │   ├─ app/templates/upload.html                                    │   │
│  │   ├─ app/templates/visualize.html                                 │   │
│  │   ├─ app/static/css/style.css (Unified Styling)                   │   │
│  │   └─ app/static/js/script.js (Client Logic)                       │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                           │
│                        HTTP Requests/Responses                               │
│                                  │                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ROUTING LAYER (FastAPI)                          │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                       │   │
│  │  app/main.py (FastAPI App Setup)                                   │   │
│  │  ├─ SessionMiddleware (User Sessions)                              │   │
│  │  ├─ Static Files Mount (/static)                                   │   │
│  │  └─ Router Includes:                                               │   │
│  │                                                                       │   │
│  │     ┌──────────────────────────────────────────────────────────┐   │   │
│  │     │ app/routers/auth_routes.py                              │   │   │
│  │     │ ├─ GET /login                                           │   │   │
│  │     │ ├─ POST /login                                          │   │   │
│  │     │ ├─ POST /signup                                         │   │   │
│  │     │ └─ GET /logout                                          │   │   │
│  │     └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │     ┌──────────────────────────────────────────────────────────┐   │   │
│  │     │ app/routers/dashboard.py                                │   │   │
│  │     └─ GET /dashboard                                          │   │   │
│  │     └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │     ┌──────────────────────────────────────────────────────────┐   │   │
│  │     │ app/routers/reports.py                                  │   │   │
│  │     │ ├─ GET /reports                                         │   │   │
│  │     │ ├─ POST /reports/create                                 │   │   │
│  │     │ ├─ DELETE /reports/{id}                                 │   │   │
│  │     │ └─ GET /api/report/{id}                                 │   │   │
│  │     └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │     ┌──────────────────────────────────────────────────────────┐   │   │
│  │     │ app/routers/upload.py                                   │   │   │
│  │     │ ├─ GET /upload                                          │   │   │
│  │     │ └─ POST /upload                                         │   │   │
│  │     └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │     ┌──────────────────────────────────────────────────────────┐   │   │
│  │     │ app/routers/visualize.py                                │   │   │
│  │     │ ├─ GET /visualize                                       │   │   │
│  │     │ ├─ GET /api/report/{id}/details                         │   │   │
│  │     │ └─ GET /api/report/{id}/export/excel                    │   │   │
│  │     └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │     ┌──────────────────────────────────────────────────────────┐   │   │
│  │     │ app/routers/qr_generation.py                            │   │   │
│  │     │ ├─ GET /qr                                              │   │   │
│  │     │ └─ POST /qr/generate                                    │   │   │
│  │     └──────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                           │
│                          Service Layer Calls                                 │
│                                  │                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   BUSINESS LOGIC LAYER (Services)                    │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                       │   │
│  │  backend/services/                                                  │   │
│  │  ├─ data_manager.py (Database CRUD)                                │   │
│  │  ├─ inferences.py (Image Processing Pipeline)                      │   │
│  │  │  ├─ Calls: google_ocr.py                                        │   │
│  │  │  ├─ Calls: annotations_parser.py                                │   │
│  │  │  ├─ Calls: detection.py                                         │   │
│  │  │  ├─ Calls: json_result.py                                       │   │
│  │  │  ├─ Calls: s3_operator.py                                       │   │
│  │  │  └─ Calls: data_manager.py → upload_result()                    │   │
│  │  ├─ google_ocr.py (Google Vision API)                              │   │
│  │  ├─ detection.py (YOLOv8 Vehicle Detection)                        │   │
│  │  ├─ annotations_parser.py (Parse OCR Results)                      │   │
│  │  ├─ json_result.py (Build Result JSON)                             │   │
│  │  ├─ s3_operator.py (AWS S3 Upload)                                 │   │
│  │  └─ qr_generation.py (QR Code Generator)                           │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                           │
│                    Database Layer & External Services                        │
│                                  │                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        DATA LAYER                                    │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │ Database: app.db (SQLite)                                  │   │   │
│  │  │                                                             │   │   │
│  │  │ backend/database.py (Connection Setup)                    │   │   │
│  │  │ backend/models/                                           │   │   │
│  │  │ ├─ report.py                                              │   │   │
│  │  │ │  └─ Report(id, name, createdAt, inferences[])          │   │   │
│  │  │ ├─ inference.py                                           │   │   │
│  │  │ │  └─ Inference(id, report_id, unique_id, vin, qty, ...) │   │   │
│  │  │ └─ record.py                                              │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │ External Services                                          │   │   │
│  │  │ ├─ Google Cloud Vision (OCR)                               │   │   │
│  │  │ ├─ AWS S3 (Image Storage)                                  │   │   │
│  │  │ ├─ Ultralytics YOLOv8 (Detection)                          │   │   │
│  │  │ └─ openpyxl (Excel Generation)                             │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │ File Storage                                               │   │   │
│  │  │ ├─ /uploads/{report_name}/ (Temporary, deleted after)      │   │   │
│  │  │ └─ /uploaded_reports/{name}_{uuid}/ (Processing)           │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Request Flow Sequence Diagrams

### 1. Report Creation Flow

```
User                    Browser              FastAPI Route           Services              Database
│                          │                      │                      │                   │
├─ Click Create Report ────>│                      │                      │                   │
│                          │                      │                      │                   │
│                          ├─ POST /reports/create │                      │                   │
│                          ├────────────────────>│                      │                   │
│                          │                      │                      │                   │
│                          │                      ├─ Validate Input       │                   │
│                          │                      │                      │                   │
│                          │                      ├─ create_report() ────>│                   │
│                          │                      │                      │                   │
│                          │                      │                      ├─ db.add(Report) ─>│
│                          │                      │                      │                   │
│                          │                      │  <─────── report_id ──│                   │
│                          │                      │                      │                   │
│                          │                      ├─ Save files to disk   │                   │
│                          │                      │                      │                   │
│                          │                      ├─ Add background task: │                   │
│                          │                      │  get_inferences(...)  │                   │
│                          │                      │                      │                   │
│                          │  <─ HTTP 303 Redirect ─                      │                   │
│                          │                      │                      │                   │
│  <─ Redirected to /reports ─                    │                      │                   │
│                          │                      │                      │                   │
│ (Background Processing)  │                      │                      │                   │
│                          │                      │                      │                   │
│                          │                      │      [Background Task Runs Asynchronously]
│                          │                      │                      │                   │
│                          │                      │                      ├─ OCR (Google) ────┤
│                          │                      │                      │                   │
│                          │                      │                      ├─ Parse IDs        │
│                          │                      │                      │                   │
│                          │                      │                      ├─ Detect (YOLOv8)  │
│                          │                      │                      │                   │
│                          │                      │                      ├─ Upload to S3     │
│                          │                      │                      │                   │
│                          │                      │                      ├─ Save Inferences ──>│
│                          │                      │                      │                   │
│                          │                      │                      ├─ Cleanup          │
│                          │                      │                      │                   │
```

### 2. Report Viewing & Excel Export Flow

```
User                    Browser              FastAPI Route           Services              Database
│                          │                      │                      │                   │
├─ Click View Details ─────>│                      │                      │                   │
│                          │                      │                      │                   │
│                          ├─ GET /visualize?report=5                      │                   │
│                          ├────────────────────>│                      │                   │
│                          │                      │                      │                   │
│                          │                      ├─ Query Report ────────>│                   │
│                          │                      │                      │                   │
│                          │                      │                      <──────────────────>│
│                          │                      │<─ selected_report ───│                   │
│                          │                      │                      │                   │
│                          │  <─ HTML Response ────│                      │                   │
│                          │                      │                      │                   │
│  ┌─ Page Loads           │                      │                      │                   │
│  │ JavaScript runs:      │                      │                      │                   │
│  │ Extract ?report=5     │                      │                      │                   │
│  │ Auto-click report     │                      │                      │                   │
│  │                       │                      │                      │                   │
│  └─>Fetch /api/report/5/details                                       │                   │
│                          │                      │                      │                   │
│                          ├─ GET /api/report/5/details                   │                   │
│                          ├────────────────────>│                      │                   │
│                          │                      │                      │                   │
│                          │                      ├─ Query Report ────────>│                   │
│                          │                      │                      │                   │
│                          │                      │  <───────────────────│                   │
│                          │                      │  Query Inferences    │                   │
│                          │                      │                      │                   │
│                          │                      │  <───────────────────│                   │
│                          │  <─ JSON Response ────│                      │                   │
│                          │                      │                      │                   │
│  Render report details   │                      │                      │                   │
│  Display images          │                      │                      │                   │
│                          │                      │                      │                   │
├─ Click Download Excel ──>│                      │                      │                   │
│                          │                      │                      │                   │
│                          ├─ GET /api/report/5/export/excel              │                   │
│                          ├────────────────────>│                      │                   │
│                          │                      │                      │                   │
│                          │                      ├─ export_report_excel()                    │
│                          │                      │  ├─ Query Report ────>│                   │
│                          │                      │  ├─ Query Inferences ──>                 │
│                          │                      │  │  <────────────────│                   │
│                          │                      │  │                      │                   │
│                          │                      │  ├─ openpyxl:        │                   │
│                          │                      │  │ Create Workbook    │                   │
│                          │                      │  │ Add Headers        │                   │
│                          │                      │  │ Add Data Rows      │                   │
│                          │                      │  │ Format Styling     │                   │
│                          │                      │  │ Add S3 Hyperlinks  │                   │
│                          │                      │  │                    │                   │
│                          │  <─ XLSX File ────────                      │                   │
│                          │                      │                      │                   │
│  Browser downloads:      │                      │                      │                   │
│  Report_5_Name.xlsx      │                      │                      │                   │
│                          │                      │                      │                   │
```

### 3. Image Processing Pipeline

```
[User uploads images]
        │
        ▼
┌──────────────────────────────────┐
│ Image Processing Pipeline        │
│ (background_tasks)               │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 1. Get image from disk           │
│    /uploads/{report_name}/       │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 2. Run OCR (Google Vision)       │
│    - Load image                  │
│    - Send to GCP API             │
│    - Get text annotations        │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 3. Parse OCR Results             │
│    - Extract Unique IDs          │
│    - Extract VIN Numbers         │
│    - Parse quantities            │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 4. Run Vehicle Detection         │
│    - Load YOLOv8 model           │
│    - Run inference on image      │
│    - Get bounding boxes          │
│    - Match with extracted IDs    │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 5. Build Result JSON             │
│    - Combine all detection data  │
│    - Create result dictionary    │
│    - Return list of results      │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 6. Upload to AWS S3              │
│    - Read image from disk        │
│    - Upload to bucket            │
│    - Get S3 URL                  │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 7. Save Results to Database      │
│    - Create Inference object     │
│    - Store all detection data    │
│    - Save S3 URL reference       │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│ 8. Cleanup Uploaded Folder       │
│    - Delete /uploads/{name}/     │
│    - Free disk space             │
└──────────────────────────────────┘
        │
        ▼
[Processing Complete - Report visible in UI]
```

---

## File Dependency Tree

```
run.py
  │
  └─> app/main.py
      ├─> app/routers/auth_routes.py
      │   ├─> app/auth/auth.py
      │   ├─> app/auth/models.py
      │   ├─> app/templates/login.html
      │   └─> app/templates/signup.html
      │
      ├─> app/routers/dashboard.py
      │   ├─> backend/database.py
      │   ├─> backend/models/report.py
      │   └─> app/templates/dashboard.html
      │
      ├─> app/routers/reports.py
      │   ├─> backend/database.py
      │   ├─> backend/models/report.py
      │   ├─> backend/models/inference.py
      │   ├─> backend/services/data_manager.py
      │   ├─> backend/services/inferences.py
      │   ├─> app/templates/reports.html
      │   └─> app/static/css/style.css
      │
      ├─> app/routers/upload.py
      │   ├─> backend/services/data_manager.py
      │   ├─> backend/services/inferences.py
      │   ├─> app/templates/upload.html
      │   └─> /uploads/ (disk storage)
      │
      ├─> app/routers/visualize.py
      │   ├─> backend/database.py
      │   ├─> backend/models/report.py
      │   ├─> backend/models/inference.py
      │   ├─> openpyxl (Excel generation)
      │   ├─> app/templates/visualize.html
      │   └─> app/static/js/script.js
      │
      ├─> app/routers/qr_generation.py
      │   ├─> backend/services/qr_generation.py
      │   └─> app/templates/qr_generation.html
      │
      ├─> app/templates/base.html
      │   ├─> app/static/css/style.css
      │   └─> app/static/js/script.js
      │
      └─> StaticFiles
          └─> app/static/


backend/services/inferences.py
  ├─> backend/services/google_ocr.py
  │   └─> Google Vision API
  │
  ├─> backend/services/annotations_parser.py
  │
  ├─> backend/services/detection.py
  │   └─> YOLOv8 (ultralytics)
  │
  ├─> backend/services/json_result.py
  │
  ├─> backend/services/s3_operator.py
  │   └─> AWS S3 (boto3)
  │
  └─> backend/services/data_manager.py
      └─> backend/database.py
          ├─> backend/models/report.py
          ├─> backend/models/inference.py
          └─> app.db (SQLite)


app/templates/base.html (Extended by all templates)
  ├─ login.html
  ├─ signup.html
  ├─ dashboard.html
  ├─ reports.html
  ├─ upload.html
  ├─ visualize.html
  ├─ qr_generation.html
  └─ report_details.html
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW IN ASRS                            │
└─────────────────────────────────────────────────────────────────────┘

User Input
    │
    ├─ Report Name
    ├─ Image Files
    └─ Filter Dates (optional)
    │
    ▼
┌──────────────────────────┐
│ Validation               │
│ - Check not empty        │
│ - Check file types       │
│ - Check file size        │
└──────────────────────────┘
    │
    ▼
┌──────────────────────────┐
│ Database Write           │
│ - Create Report record   │
│ - Get report_id          │
└──────────────────────────┘
    │
    ├─────────────────────────────────────┬──────────────────────────┐
    │                                     │                          │
    ▼                                     ▼                          ▼
┌──────────────┐                ┌──────────────────┐    ┌────────────────┐
│ Sync Path    │                │ Async Path       │    │ Data Storage   │
│              │                │ (Background)     │    │                │
│ Save Files   │                │                  │    │ /uploads/      │
│ to Disk      │                │ Process Images:  │    │ /uploaded_     │
│ /uploads/    │                │ - OCR            │    │   reports/     │
│              │                │ - Detection      │    │ /results/      │
└──────────────┘                │ - Upload to S3   │    │                │
    │                           │ - Save Inferences│    │ Database:      │
    │                           │ - Cleanup        │    │ app.db         │
    │                           │                  │    │ - Reports      │
    │                           └──────────────────┘    │ - Inferences   │
    │                                                    │ - Records      │
    └─────────────────────────────────────────────────>┤                │
                                                        └────────────────┘
                                                            │
                                                            ▼
                                                    ┌──────────────────┐
                                                    │ External APIs    │
                                                    │                  │
                                                    │ Google Vision    │
                                                    │ AWS S3           │
                                                    │ YOLOv8           │
                                                    │ openpyxl         │
                                                    └──────────────────┘
                                                            │
                                                            ▼
                                                    ┌──────────────────┐
                                                    │ Output Data      │
                                                    │                  │
                                                    │ - Images in S3   │
                                                    │ - OCR Results    │
                                                    │ - Detection Data │
                                                    │ - Excel Reports  │
                                                    │ - QR Codes       │
                                                    └──────────────────┘
```

---

## Class/Model Relationships

```
┌─────────────────────────────────────────────────────────────────────┐
│                       DATABASE SCHEMA                               │
└─────────────────────────────────────────────────────────────────────┘

Report Table
┌──────────────────────────────┐
│ id (PK)                      │
│ report_name (str)            │
│ createdAt (datetime)         │◄───┐
│ inferences (Relationship)    │    │
└──────────────────────────────┘    │ One-to-Many
                                     │
Inference Table                      │
┌──────────────────────────────┐    │
│ id (PK)                      │    │
│ report_id (FK) ──────────────┼────┘
│ image_name (str)             │
│ unique_id (str)              │
│ vin_no (str)                 │
│ quantity (int)               │
│ exclusion (str)              │
│ is_non_conformity (bool)     │
│ s3_obj_url (str) ◄───┬─── Link to AWS S3
│ createdAt (datetime)         │
└──────────────────────────────┘

Record Table
┌──────────────────────────────┐
│ id (PK)                      │
│ (Helper for detection)       │
└──────────────────────────────┘

User Table (Authentication)
┌──────────────────────────────┐
│ id (PK)                      │
│ username (str)               │
│ hashed_password (str)        │
└──────────────────────────────┘
```

---

## Component Interaction Matrix

```
┌──────────┬──────────┬─────────┬──────────┬──────────┬─────────────┐
│ Component│ Database │ Routes  │ Services │ Templates│ External    │
├──────────┼──────────┼─────────┼──────────┼──────────┼─────────────┤
│ Models   │   ✓      │         │    ✓     │          │             │
│ Routes   │   ✓      │    ✓    │    ✓     │    ✓     │     ✓       │
│ Services │   ✓      │         │    ✓     │          │     ✓       │
│Templates │          │         │          │    ✓     │             │
│ Static   │          │         │          │    ✓     │             │
└──────────┴──────────┴─────────┴──────────┴──────────┴─────────────┘

✓ = Imports/Uses/Calls
```

---

## Performance Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              REQUEST PROCESSING TIMELINE                         │
└─────────────────────────────────────────────────────────────────┘

Fast Path (Synchronous):
    POST /reports/create
    ├─ Validation: 10ms
    ├─ DB write: 50ms
    ├─ File save: 500ms (depends on file size)
    └─ Queue task: 1ms
    Total: ~561ms → Return to user

Slow Path (Asynchronous - Background):
    get_inferences() [Background]
    ├─ For each image:
    │  ├─ OCR (Google): 2-5 seconds (network dependent)
    │  ├─ Parse: 100ms
    │  ├─ Detection (YOLOv8): 1-3 seconds (model dependent)
    │  ├─ S3 Upload: 500ms - 2s (file size dependent)
    │  └─ DB write: 50ms
    ├─ Cleanup: 100ms
    └─ Total per image: 4-11 seconds
    
User Experience: Sees success message immediately, report appears
as images are processed (or all at once when done)
```

---

**Version:** 1.0  
**Created:** December 14, 2025  
**For:** ASRS Development Team
