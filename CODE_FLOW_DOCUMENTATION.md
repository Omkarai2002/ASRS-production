# ASRS Application - Complete Code Flow Documentation

## 📋 Table of Contents
1. [Application Entry Points](#application-entry-points)
2. [Project Structure Overview](#project-structure-overview)
3. [Detailed Module Flow](#detailed-module-flow)
4. [Database Layer](#database-layer)
5. [Request-Response Flow](#request-response-flow)
6. [Authentication Flow](#authentication-flow)
7. [Report Creation & Processing Flow](#report-creation--processing-flow)
8. [File Dependencies Map](#file-dependencies-map)

---

## 🚀 Application Entry Points

### 1. Server Startup: `run.py`
```
run.py (Entry Point)
    │
    └─> uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
            │
            └─> Starts FastAPI application on http://127.0.0.1:8000
```

### 2. Application Initialization: `app/main.py`
```
app/main.py (FastAPI Application Setup)
    │
    ├─> FastAPI() instance created
    │
    ├─> SessionMiddleware added (for user session management)
    │
    ├─> Static files mounted (CSS, JS, images)
    │   └─> /static → app/static/
    │
    ├─> Templates configured (Jinja2)
    │   └─> app/templates/
    │
    └─> Routers included (6 router modules):
        ├─> auth_routes.py      → /login, /signup, /logout
        ├─> dashboard.py        → /dashboard
        ├─> reports.py          → /reports, /reports/create, /api/report/{id}
        ├─> upload.py           → /upload
        ├─> visualize.py        → /visualize, /api/report/{id}/details, /api/report/{id}/export/excel
        └─> qr_generation.py    → /qr
```

---

## 📁 Project Structure Overview

```
ASRS-prod/
│
├── app/                          # Frontend & API routes
│   ├── main.py                   # FastAPI app setup & router registration
│   ├── auth/                     # Authentication module
│   │   ├── auth.py              # User authentication functions
│   │   ├── models.py            # User model
│   │   └── __init__.py
│   │
│   ├── routers/                  # API route handlers
│   │   ├── auth_routes.py       # GET /login, POST /login, POST /signup, GET /logout
│   │   ├── dashboard.py         # GET /dashboard
│   │   ├── reports.py           # GET /reports, POST /reports/create, DELETE /reports/{id}
│   │   ├── upload.py            # POST /upload
│   │   ├── visualize.py         # GET /visualize, GET /api/report/{id}/details, GET /api/report/{id}/export/excel
│   │   ├── qr_generation.py     # GET /qr, POST /qr/generate
│   │   └── visualization.py     # Visualization helper functions
│   │
│   ├── static/                   # Static assets (served as-is)
│   │   ├── css/
│   │   │   └── style.css        # Unified CSS framework
│   │   ├── js/
│   │   │   └── script.js        # Client-side JavaScript
│   │   └── images/              # Image assets
│   │
│   └── templates/                # Jinja2 HTML templates
│       ├── base.html            # Base template (navbar, footer, CSS variables)
│       ├── login.html           # Login page
│       ├── signup.html          # User registration
│       ├── dashboard.html       # Dashboard overview
│       ├── reports.html         # Reports list with create form
│       ├── upload.html          # File upload page
│       ├── visualize.html       # Report details & visualization
│       ├── qr_generation.html   # QR code generation
│       └── report_details.html  # Individual report details
│
├── backend/                      # Data processing & business logic
│   ├── database.py              # Database connection & session management
│   │
│   ├── models/                   # Database models (SQLModel)
│   │   ├── report.py            # Report model
│   │   ├── inference.py         # Inference model
│   │   └── record.py            # Record model
│   │
│   └── services/                 # Business logic services
│       ├── data_manager.py      # Database CRUD operations
│       ├── inferences.py        # Image processing & inference
│       ├── detection.py         # Vehicle detection (YOLOv8)
│       ├── google_ocr.py        # Google Vision OCR
│       ├── annotations_parser.py# Parse OCR results
│       ├── json_result.py       # Build result JSON
│       ├── s3_operator.py       # AWS S3 upload
│       └── qr_generation.py     # QR code generation
│
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
├── app.db                        # SQLite database
└── .env                          # Environment variables

```

---

## 🔄 Detailed Module Flow

### Module 1: Authentication Module (`app/auth/`)
```
User Request to /login or /signup
    │
    ├─> auth_routes.py (app/routers/auth_routes.py)
    │   │
    │   ├─> GET /login  → Renders login.html template
    │   │
    │   ├─> POST /login (Form: username, password)
    │   │   │
    │   │   └─> auth.py (app/auth/auth.py)
    │   │       │
    │   │       ├─> verify_password() → Check hashed password
    │   │       │
    │   │       ├─> authenticate_user() → Query User from DB
    │   │       │   │
    │   │       │   └─> backend.models.User (SQLModel)
    │   │       │       │
    │   │       │       └─> backend.database.SessionLocal()
    │   │       │           └─> app.db (SQLite)
    │   │       │
    │   │       └─> Sets request.session["user"] = username
    │   │           Redirects to /dashboard
    │   │
    │   └─> POST /signup (Form: username, password)
    │       │
    │       └─> Creates new User, hashes password
    │           Saves to database
    │           Redirects to /login
    │
    └─> GET /logout → Clears session, Redirects to /login
```

### Module 2: Dashboard Module (`app/routers/dashboard.py`)
```
User Request to /dashboard
    │
    ├─> Check authentication (session["user"] required)
    │
    ├─> Query statistics from database:
    │   ├─> Total reports count
    │   ├─> Total items detected
    │   ├─> Reports created today
    │   └─> System status
    │
    └─> Render dashboard.html with stats & chart data
        │
        └─> Template displays:
            ├─> Statistics cards with icons
            ├─> Activity chart (Chart.js)
            └─> Quick action buttons
```

### Module 3: Reports Module (`app/routers/reports.py`)
```
GET /reports
    │
    ├─> Check authentication
    │
    ├─> Query all reports from database
    │   │
    │   ├─> backend.database.SessionLocal()
    │   │   └─> app.db (SQLite)
    │   │
    │   └─> backend.models.report.Report (SQLModel)
    │       └─> Joined with Inference count
    │           └─> backend.models.inference.Inference
    │
    ├─> Order by createdAt DESC (latest first)
    │
    └─> Render reports.html with:
        ├─> Report list in card grid
        ├─> Create report form
        ├─> Search & date range filters
        └─> View Details & Delete buttons


POST /reports/create (Form: report_name, files[])
    │
    ├─> Validate inputs (name not empty, files provided)
    │
    ├─> Create report in database
    │   │
    │   └─> backend.services.data_manager.create_report(report_name)
    │       │
    │       ├─> backend.database.SessionLocal()
    │       ├─> backend.models.report.Report() instance created
    │       └─> db.add() & db.commit()
    │
    ├─> Save uploaded files to disk
    │   │
    │   └─> /uploads/{sanitized_report_name}/
    │
    ├─> Queue background processing task
    │   │
    │   └─> background_tasks.add_task(get_inferences, report_dir, report_id)
    │
    └─> Redirect to /reports with success message


DELETE /reports/{report_id}
    │
    ├─> Query and delete report from database
    │
    ├─> Delete all associated inferences
    │
    └─> Redirect to /reports with success message


GET /api/report/{report_id}
    │
    ├─> JSON API endpoint
    │
    ├─> Return report details & all inferences
    │   ├─> Report ID, name, creation date
    │   └─> Inference list with all fields
    │
    └─> Used by JavaScript/AJAX for dynamic content
```

### Module 4: Upload Module (`app/routers/upload.py`)
```
GET /upload
    │
    └─> Render upload.html form
        │
        └─> Form shows:
            ├─> Report name input
            ├─> File upload (drag-drop)
            └─> Progress bar placeholder


POST /upload (Form: report_name, files[])
    │
    ├─> Create database report entry
    │   └─> backend.services.data_manager.create_report()
    │
    ├─> Save files to disk
    │   └─> /uploaded_reports/{safe_name}_{uuid}/
    │
    ├─> Queue background processing
    │   └─> background_tasks.add_task(get_inferences, report_dir, report_id)
    │
    └─> Display success message with report ID
```

### Module 5: Visualization Module (`app/routers/visualize.py`)
```
GET /visualize?report={report_id}
    │
    ├─> Check authentication
    │
    ├─> Get all reports (for sidebar list)
    │   └─> backend.models.report.Report
    │
    ├─> If report_id parameter provided:
    │   │
    │   ├─> Auto-load that specific report
    │   │   └─> Fetch report data
    │   │
    │   └─> Return selected_report in template context
    │       └─> JavaScript auto-clicks that report on page load
    │
    └─> Render visualize.html with:
        ├─> Left panel: Reports list with search & date filters
        └─> Right panel: Empty or pre-loaded report details


GET /api/report/{report_id}/details (JSON API)
    │
    ├─> Query report from database
    │
    ├─> Query all inferences for that report
    │   └─> Order by createdAt DESC
    │
    └─> Return JSON with:
        ├─> Report info (name, date, count)
        ├─> Inference array with all data
        ├─> S3 URLs for images
        └─> Status information


GET /api/report/{report_id}/export/excel (DOWNLOAD)
    │
    ├─> Query report & inferences
    │
    ├─> Create Workbook (openpyxl)
    │   │
    │   ├─> Add report header section
    │   │   ├─> Report name
    │   │   ├─> Creation date
    │   │   └─> Total items count
    │   │
    │   ├─> Create formatted table
    │   │   ├─> Headers: Item #, ID, VIN, Qty, Image, Exclusion, Status, Date, Download
    │   │   └─> Data rows: One per inference
    │   │       └─> S3 URL as hyperlink in "Download" column
    │   │
    │   └─> Apply styling
    │       ├─> Header colors (#667eea)
    │       ├─> Borders and alignment
    │       └─> Column width auto-adjustment
    │
    └─> Return as downloadable XLSX file
        └─> Filename: Report_{id}_{name}.xlsx
```

### Module 6: QR Generation Module (`app/routers/qr_generation.py`)
```
GET /qr
    │
    ├─> Check authentication
    │
    ├─> Get all reports for dropdown
    │
    └─> Render qr_generation.html


POST /qr/generate (Form: report_id)
    │
    ├─> Validate report exists
    │
    ├─> Generate QR code from report data
    │   │
    │   └─> backend.services.qr_generation.generate_qr()
    │       │
    │       ├─> Uses qrcode library
    │       │
    │       └─> Creates QR code image
    │
    └─> Return QR code as PNG image response
```

---

## 💾 Database Layer

### Database Connection: `backend/database.py`
```
app starts
    │
    └─> backend/database.py
        │
        ├─> Import SQLAlchemy
        │
        ├─> DATABASE_URL = "sqlite:///./app.db"
        │
        ├─> engine = create_engine(DATABASE_URL)
        │
        ├─> SessionLocal = sessionmaker(bind=engine)
        │
        └─> Base = declarative_base()  # For model inheritance
            │
            └─> Used by all models to define tables
```

### Database Models: `backend/models/`

#### 1. Report Model (`backend/models/report.py`)
```
Report (SQLModel)
    │
    ├─> id: int (Primary Key)
    ├─> report_name: str
    ├─> createdAt: datetime
    └─> Relationship: inferences (One-to-Many with Inference)
        │
        └─> One report can have many inferences
```

#### 2. Inference Model (`backend/models/inference.py`)
```
Inference (SQLModel)
    │
    ├─> id: int (Primary Key)
    ├─> report_id: int (Foreign Key → Report.id)
    ├─> image_name: str
    ├─> unique_id: str
    ├─> vin_no: str
    ├─> quantity: int
    ├─> exclusion: str
    ├─> is_non_confirmity: bool
    ├─> s3_obj_url: str  ← URL to image in S3
    ├─> createdAt: datetime
    └─> Relationship: report (Many-to-One with Report)
        │
        └─> Many inferences belong to one report
```

#### 3. Record Model (`backend/models/record.py`)
```
Record (SQLModel)
    │
    ├─> Used for storing raw VIN/ID detection data
    └─> Helper model for detection pipeline
```

### Service Layer: `backend/services/`

#### Data Manager: `backend/services/data_manager.py`
```
Database CRUD Operations
    │
    ├─> create_report(name)
    │   └─> Inserts new Report into database
    │
    ├─> get_reports()
    │   └─> Query all reports from database
    │
    ├─> get_inferences(report_id)
    │   └─> Query all inferences for a report
    │
    └─> upload_result(inference)
        └─> Insert Inference record into database
```

#### Image Processing: `backend/services/inferences.py`
```
get_inferences(report_dir, report_id)
    │
    ├─> For each image in report_dir:
    │   │
    │   ├─> process_single_image(image_path)
    │   │   │
    │   │   ├─> Call Google OCR
    │   │   │   └─> google_ocr.py → get_annotations()
    │   │   │       └─> Google Vision API
    │   │   │
    │   │   ├─> Parse OCR results
    │   │   │   └─> annotations_parser.py → get_unique_ids()
    │   │   │       └─> Extract IDs from OCR text
    │   │   │
    │   │   ├─> Run vehicle detection
    │   │   │   └─> detection.py → detect_vehicle()
    │   │   │       └─> YOLOv8 model (ultralytics)
    │   │   │
    │   │   └─> Build result JSON
    │   │       └─> json_result.py → build_result()
    │   │           └─> Combine all detection data
    │   │
    │   ├─> Upload image to S3
    │   │   └─> s3_operator.py → upload_images()
    │   │       └─> AWS S3 (boto3)
    │   │
    │   └─> Save inference to database
    │       └─> data_manager.py → upload_result(Inference)
    │
    ├─> After all images processed:
    │   │
    │   └─> Cleanup uploaded folder (try/finally)
    │       └─> shutil.rmtree(report_dir)
    │           └─> Delete /uploads/{report_name}/
    │
    └─> Processing complete, report visible in UI
```

#### OCR Service: `backend/services/google_ocr.py`
```
OCRClient.get_annotations(image_path)
    │
    ├─> Load image from file
    │
    ├─> Create Vision API client (GCP credentials)
    │   └─> GoogleVisionCredential.json
    │
    ├─> Send image to Google Vision API
    │
    └─> Return text annotations (OCR results)
```

#### Detection Service: `backend/services/detection.py`
```
detect_vehicle(image_path, unique_ids)
    │
    ├─> Load YOLOv8 model (ultralytics)
    │
    ├─> Run detection on image
    │   └─> Get bounding boxes, confidence scores
    │
    ├─> Match detections with extracted IDs
    │
    └─> Return detection results (quantities, locations)
```

#### S3 Upload: `backend/services/s3_operator.py`
```
upload_images(image_path)
    │
    ├─> Initialize S3 client (boto3)
    │
    ├─> Read image file
    │
    ├─> Upload to AWS S3 bucket
    │   └─> /inspections/{report_id}/{image_name}
    │
    └─> Return S3 URL & S3 key
        └─> s3_obj_url stored in Inference model
```

#### QR Generation: `backend/services/qr_generation.py`
```
generate_qr(report_data)
    │
    ├─> Encode report data to QR code
    │
    ├─> Use qrcode library
    │
    └─> Return QR code image
```

---

## 🔐 Authentication Flow

```
User visits http://localhost:8000
    │
    ├─> app/main.py root() route
    │
    ├─> Check if request.session["user"] exists
    │
    ├─> If NO session (not logged in):
    │   │
    │   └─> Redirect to /login
    │       │
    │       └─> auth_routes.py (GET /login)
    │           │
    │           └─> Render login.html
    │               │
    │               ├─> Form with username & password fields
    │               │
    │               └─> On submit → POST /login
    │                   │
    │                   ├─> auth.py → authenticate_user(username, password)
    │                   │   │
    │                   │   ├─> Query User from database
    │                   │   │
    │                   │   ├─> Verify password hash (bcrypt)
    │                   │   │
    │                   │   └─> Return True/False
    │                   │
    │                   ├─> If authenticated:
    │                   │   │
    │                   │   ├─> Set request.session["user"] = username
    │                   │   │
    │                   │   └─> Redirect to /dashboard
    │                   │
    │                   └─> If not authenticated:
    │                       │
    │                       └─> Redirect to /login with error message
    │
    └─> If YES session exists (logged in):
        │
        └─> Redirect to /dashboard
            │
            └─> dashboard.py (GET /dashboard)
                │
                └─> Render dashboard.html with stats
```

### Session Middleware
```
app/main.py
    │
    ├─> SessionMiddleware(secret_key=SECRET_KEY)
    │   │
    │   ├─> Manages user sessions via secure cookies
    │   │
    │   ├─> Stores: request.session["user"] = username
    │   │
    │   └─> Used in all routes to check authentication
    │
    └─> Applied to all routes automatically
        │
        └─> If session["user"] not found → redirect to /login
```

---

## 📤 Report Creation & Processing Flow

### Complete End-to-End Flow

```
USER CREATES REPORT
    │
    1. User on /reports page
    │
    2. Fills form: Report Name, Selects Images
    │   └─> reports.html (CREATE REPORT form)
    │
    3. Submits form (POST /reports/create)
    │   │
    │   └─> app/routers/reports.py
    │
    4. Server-side processing:
    │   │
    │   ├─> Validate inputs
    │   │   ├─> report_name not empty
    │   │   └─> files list not empty
    │   │
    │   ├─> Create report in database
    │   │   │
    │   │   ├─> backend/services/data_manager.py
    │   │   │   │
    │   │   │   ├─> SessionLocal() → database session
    │   │   │   │
    │   │   │   ├─> Report(report_name=name) → new model instance
    │   │   │   │
    │   │   │   ├─> db.add(report)
    │   │   │   │
    │   │   │   ├─> db.commit()
    │   │   │   │
    │   │   │   └─> return report.id
    │   │   │
    │   │   └─> report_id saved to variable
    │   │
    │   ├─> Save uploaded files to disk
    │   │   │
    │   │   ├─> Sanitize folder name
    │   │   │
    │   │   ├─> Create /uploads/{sanitized_name}/
    │   │   │
    │   │   ├─> For each file:
    │   │   │   │
    │   │   │   ├─> await file.read() → get file content
    │   │   │   │
    │   │   │   └─> Write to /uploads/{sanitized_name}/{filename}
    │   │   │
    │   │   └─> report_dir path saved
    │   │
    │   └─> Queue background task
    │       │
    │       └─> background_tasks.add_task(get_inferences, report_dir, report_id)
    │           │
    │           └─> Task runs asynchronously (doesn't block response)
    │
    5. Server responds with redirect
    │   └─> HTTP 303 → /reports?success=Report created
    │
    6. User sees success message on /reports page
    │   └─> "Report created successfully"

================================================================================
BACKGROUND PROCESSING (Happens asynchronously)
================================================================================

backend/services/inferences.py → get_inferences(report_dir, report_id)
    │
    ├─> START: try block
    │
    ├─> For each file in report_dir:
    │   │
    │   ├─> Filter: only .jpg, .png, .jpeg files
    │   │
    │   ├─> Construct: image_path = report_dir + filename
    │   │
    │   ├─> PROCESS IMAGE:
    │   │   │
    │   │   ├─> process_single_image(image_path)
    │   │   │   │
    │   │   │   ├─> STEP 1: Run OCR
    │   │   │   │   │
    │   │   │   │   └─> google_ocr.py
    │   │   │   │       │
    │   │   │   │       ├─> Load Google Vision credentials
    │   │   │   │       │   └─> GoogleVisionCredential.json
    │   │   │   │       │
    │   │   │   │       ├─> Create Vision API client
    │   │   │   │       │
    │   │   │   │       ├─> Send image to Google Vision API
    │   │   │   │       │
    │   │   │   │       └─> Return: annotations (text detected)
    │   │   │   │
    │   │   │   ├─> STEP 2: Parse OCR Results
    │   │   │   │   │
    │   │   │   │   └─> annotations_parser.py
    │   │   │   │       │
    │   │   │   │       ├─> Extract unique IDs from OCR text
    │   │   │   │       │
    │   │   │   │       └─> Return: [ID1, ID2, ID3, ...]
    │   │   │   │
    │   │   │   ├─> STEP 3: Run Vehicle Detection
    │   │   │   │   │
    │   │   │   │   └─> detection.py
    │   │   │   │       │
    │   │   │   │       ├─> Load YOLOv8 model (pre-trained)
    │   │   │   │       │
    │   │   │   │       ├─> Run inference on image
    │   │   │   │       │
    │   │   │   │       ├─> Get bounding boxes & confidence scores
    │   │   │   │       │
    │   │   │   │       ├─> Match with extracted IDs
    │   │   │   │       │
    │   │   │   │       └─> Return: detection results with quantities
    │   │   │   │
    │   │   │   └─> STEP 4: Build Result JSON
    │   │   │       │
    │   │   │       └─> json_result.py
    │   │   │           │
    │   │   │           ├─> Combine: image name + unique IDs + detection data
    │   │   │           │
    │   │   │           └─> Return: List of result dicts
    │   │   │               [
    │   │   │                 {
    │   │   │                   "IMG_NAME": "image1.jpg",
    │   │   │                   "UNIQUE_ID": "ID123",
    │   │   │                   "QUANTITY": 2,
    │   │   │                   "VIN_NO": "ABC123",
    │   │   │                   "EXCLUSION": "None"
    │   │   │                 },
    │   │   │                 ...
    │   │   │               ]
    │   │   │
    │   │   ├─> STEP 5: Upload Image to S3
    │   │   │   │
    │   │   │   └─> s3_operator.py
    │   │   │       │
    │   │   │       ├─> Initialize AWS S3 client (boto3)
    │   │   │       │   └─> Credentials from .env file
    │   │   │       │
    │   │   │       ├─> Upload image file to S3 bucket
    │   │   │       │   └─> /inspections/{report_id}/{image_name}
    │   │   │       │
    │   │   │       └─> Return: (s3_key, s3_url)
    │   │   │
    │   │   └─> STEP 6: Save Inferences to Database
    │   │       │
    │   │       └─> For each result dict:
    │   │           │
    │   │           ├─> Create Inference object
    │   │           │   │
    │   │           │   ├─> Inference(
    │   │           │   │     report_id = report_id,
    │   │           │   │     image_name = result["IMG_NAME"],
    │   │           │   │     unique_id = result["UNIQUE_ID"],
    │   │           │   │     vin_no = result["VIN_NO"],
    │   │           │   │     quantity = result["QUANTITY"],
    │   │           │   │     s3_obj_url = s3_url,
    │   │           │   │     ...
    │   │           │   │   )
    │   │           │
    │   │           └─> data_manager.py → upload_result(inference)
    │   │               │
    │   │               ├─> db.add(inference)
    │   │               │
    │   │               └─> db.commit()
    │
    ├─> FINALLY: finally block (runs regardless of success/error)
    │   │
    │   ├─> Check: if report_dir exists
    │   │   │
    │   │   ├─> YES:
    │   │   │   │
    │   │   │   └─> shutil.rmtree(report_dir)
    │   │   │       │
    │   │   │       ├─> Recursively delete entire folder
    │   │   │       │   └─> /uploads/{sanitized_name}/
    │   │   │       │
    │   │   │       └─> Log: "Cleaned up processed folder: /uploads/{name}"
    │   │   │
    │   │   └─> NO: Skip cleanup
    │   │
    │   └─> Print success/error message to console
    │
    └─> END: Background task complete
        │
        └─> User can now see:
            ├─> Report on /reports page
            ├─> Report details on /visualize page
            └─> All inferences with S3 image URLs


VIEWING & EXPORTING REPORT
    │
    1. User on /reports page, clicks "View Details" for Report #5
    │   └─> <a href="/visualize?report=5">
    │
    2. Browser navigates to /visualize?report=5
    │   │
    │   └─> app/routers/visualize.py (GET /visualize?report=5)
    │
    3. Server-side rendering:
    │   │
    │   ├─> Parse query parameter: report_id = 5
    │   │
    │   ├─> Query report from database
    │   │   └─> backend.models.Report (id=5)
    │   │
    │   ├─> Query all inferences for this report
    │   │   └─> backend.models.Inference (report_id=5)
    │   │
    │   ├─> Build report data object
    │   │   ├─> Report info (name, date, count)
    │   │   └─> Inferences array (all fields + S3 URLs)
    │   │
    │   └─> Pass to template context:
    │       ├─> selected_report = report_data
    │       ├─> selected_report_id = 5
    │       └─> all_reports = [...all reports for sidebar...]
    │
    4. Page renders with template variables
    │   │
    │   └─> visualize.html
    │
    5. JavaScript auto-load on page load:
    │   │
    │   ├─> Extract URL param: report_id = 5
    │   │
    │   ├─> Find report item in sidebar: [data-report-id="5"]
    │   │
    │   └─> Auto-click that item
    │       │
    │       └─> Triggers loadReport(5) function
    │
    6. loadReport() JavaScript function:
    │   │
    │   ├─> Fetch /api/report/5/details (JSON)
    │   │
    │   ├─> Receive JSON response:
    │   │   ├─> Report name, creation date, item count
    │   │   └─> Inferences array with all data
    │   │
    │   ├─> Generate HTML with:
    │   │   ├─> Report header info
    │   │   ├─> "Download Excel" button
    │   │   ├─> Images grid with inference details
    │   │   └─> S3 image URLs
    │   │
    │   └─> Update page with generated HTML
    │
    7. User sees fully loaded report details
    │   │
    │   └─> With all inferences displayed
    │
    8. User clicks "Download Excel" button
    │   │
    │   └─> GET /api/report/5/export/excel
    │
    9. Server-side Excel generation:
    │   │
    │   ├─> openpyxl.Workbook() → New Excel workbook
    │   │
    │   ├─> Add sheet "Report Data"
    │   │
    │   ├─> Add header section:
    │   │   ├─> Cell A1: "Report: Report Name"
    │   │   ├─> Cell A2: "Created: 2025-12-14"
    │   │   └─> Cell A3: "Total Items: 10"
    │   │
    │   ├─> Add formatted table header (Row 5):
    │   │   ├─> Column A: Item #
    │   │   ├─> Column B: Unique ID
    │   │   ├─> Column C: VIN Number
    │   │   ├─> Column D: Quantity
    │   │   ├─> Column E: Image Name
    │   │   ├─> Column F: Exclusion
    │   │   ├─> Column G: Non-Conformity
    │   │   ├─> Column H: Created Date
    │   │   └─> Column I: Download Image
    │   │
    │   ├─> For each inference (Row 6+):
    │   │   ├─> A6: 1
    │   │   ├─> B6: "ID123"
    │   │   ├─> C6: "ABC123"
    │   │   ├─> D6: 2
    │   │   ├─> E6: "image1.jpg"
    │   │   ├─> F6: "None"
    │   │   ├─> G6: "No"
    │   │   ├─> H6: "2025-12-14 10:30:00"
    │   │   └─> I6: "Download" (hyperlink to S3 URL)
    │   │
    │   ├─> Apply styling:
    │   │   ├─> Header: Blue background (#667eea), white text, bold
    │   │   ├─> Borders: All cells have borders
    │   │   └─> Width: Auto-adjusted per column
    │   │
    │   ├─> Save to BytesIO (in-memory)
    │   │
    │   └─> Return as StreamingResponse:
    │       ├─> Media type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    │       └─> Filename: Report_5_ReportName.xlsx
    │
    10. Browser downloads Excel file
    │   │
    │   └─> User opens in Excel, Google Sheets, or LibreOffice
    │
    11. User views Excel with all report data
    │   │
    │   ├─> Professional formatting
    │   ├─> All inferences visible
    │   └─> Can click download links to view images from S3
```

---

## 📊 File Dependencies Map

### Request Flow Dependencies

```
HTTP Request
    │
    ├─> FastAPI router (app/routers/*.py)
    │   │
    │   ├─> Imports templates: from fastapi.templating import Jinja2Templates
    │   │   └─> app/templates/*.html
    │   │
    │   ├─> Imports database: from backend.database import SessionLocal
    │   │   └─> backend/database.py
    │   │       └─> Import app.db
    │   │
    │   ├─> Imports models: from backend.models.*.py
    │   │   ├─> backend/models/report.py
    │   │   ├─> backend/models/inference.py
    │   │   └─> backend/models/record.py
    │   │
    │   └─> Imports services: from backend.services.*.py
    │       ├─> backend/services/data_manager.py
    │       ├─> backend/services/inferences.py
    │       ├─> backend/services/google_ocr.py
    │       ├─> backend/services/detection.py
    │       ├─> backend/services/s3_operator.py
    │       └─> backend/services/json_result.py
    │
    └─> Response
        ├─> HTML Template (Jinja2 rendering)
        ├─> JSON Response
        ├─> File Download (Excel, PNG)
        └─> Redirect
```

### File Import Tree

```
app/main.py
    │
    ├─> from .routers import (
    │   ├─> dashboard.py
    │   ├─> reports.py
    │   │   └─> Imports: backend.database, backend.models, backend.services
    │   ├─> upload.py
    │   ├─> visualize.py
    │   │   └─> Imports: backend.database, backend.models, openpyxl
    │   ├─> auth_routes.py
    │   │   └─> Imports: backend.auth, backend.models.user
    │   └─> qr_generation.py
    │       └─> Imports: backend.services.qr_generation
    │
    ├─> from starlette.middleware.sessions import SessionMiddleware
    │
    ├─> from fastapi.staticfiles import StaticFiles
    │   └─> Serves: app/static/
    │
    └─> from fastapi.templating import Jinja2Templates
        └─> Loads: app/templates/


backend/database.py
    │
    ├─> from sqlalchemy import create_engine
    │
    ├─> from sqlalchemy.orm import sessionmaker
    │
    └─> Models import this:
        ├─> backend/models/report.py
        ├─> backend/models/inference.py
        └─> backend/models/record.py


backend/services/inferences.py
    │
    ├─> from backend.services.google_ocr import OCRClient
    │
    ├─> from backend.services.annotations_parser import AnnotationsParser
    │
    ├─> from backend.services.detection import detect_vehicle
    │
    ├─> from backend.services.json_result import build_result
    │
    ├─> from backend.services.s3_operator import upload_images
    │
    ├─> from backend.services.data_manager import upload_result
    │
    └─> import shutil (for cleanup)


app/templates/base.html
    │
    ├─> Linked to: app/static/css/style.css
    │
    ├─> Linked to: app/static/js/script.js
    │
    └─> Extended by:
        ├─> login.html
        ├─> signup.html
        ├─> dashboard.html
        ├─> reports.html
        ├─> upload.html
        ├─> visualize.html
        ├─> qr_generation.html
        └─> report_details.html
```

---

## 🔌 API Endpoints Summary

```
Authentication Routes (app/routers/auth_routes.py):
    GET    /login                           → Render login.html
    POST   /login                           → Authenticate user
    POST   /signup                          → Create new user
    GET    /logout                          → Clear session

Dashboard Route (app/routers/dashboard.py):
    GET    /dashboard                       → Render dashboard.html

Reports Routes (app/routers/reports.py):
    GET    /reports                         → List all reports
    POST   /reports/create                  → Create new report
    POST   /reports/{id}/delete             → Delete report
    GET    /api/report/{id}                 → JSON: Report details

Visualization Routes (app/routers/visualize.py):
    GET    /visualize                       → Report visualization page
    GET    /api/report/{id}/details         → JSON: All inferences
    GET    /api/report/{id}/export/excel    → Download Excel file

Upload Route (app/routers/upload.py):
    GET    /upload                          → Render upload.html
    POST   /upload                          → Upload files & create report

QR Generation Routes (app/routers/qr_generation.py):
    GET    /qr                              → QR generation page
    POST   /qr/generate                     → Generate QR code
```

---

## 🚀 How to Follow Code Execution

### Example: User Creates a Report

**Start:** User clicks "Create Report" button
```
1. Open: app/templates/reports.html (Search for: class="create-section")
2. Find: <form method="post" action="/reports/create" ...>
3. Follow: POST endpoint in app/routers/reports.py
   └─> Find: @router.post("/reports/create")
4. Inside create_report_endpoint():
   └─> Find: create_report(report_name)
5. Open: backend/services/data_manager.py
   └─> Find: def create_report(name)
6. See: Creates Report, adds to DB, commits
7. Back to reports.py:
   └─> background_tasks.add_task(get_inferences, ...)
8. Open: backend/services/inferences.py
   └─> Find: def get_inferences(report_dir, report_id)
9. Inside, find: process_single_image(image_path)
10. This calls multiple services in sequence:
    ├─> google_ocr.py
    ├─> annotations_parser.py
    ├─> detection.py
    ├─> json_result.py
    ├─> s3_operator.py
    └─> data_manager.py (upload_result)
```

---

## 📚 Quick Reference

| File | Purpose | Main Functions |
|------|---------|-----------------|
| `run.py` | Entry point | `uvicorn.run()` |
| `app/main.py` | App setup | Router registration, middleware |
| `app/routers/reports.py` | Reports CRUD | `reports_page()`, `create_report_endpoint()` |
| `app/routers/visualize.py` | Report visualization | `visualize_reports()`, `export_report_excel()` |
| `backend/database.py` | DB connection | `SessionLocal`, `engine` |
| `backend/models/report.py` | Report model | Report table schema |
| `backend/models/inference.py` | Inference model | Inference table schema |
| `backend/services/inferences.py` | Image processing | `get_inferences()`, `process_single_image()` |
| `backend/services/google_ocr.py` | OCR service | `OCRClient.get_annotations()` |
| `backend/services/detection.py` | Vehicle detection | `detect_vehicle()` |
| `backend/services/s3_operator.py` | S3 upload | `upload_images()` |
| `app/templates/reports.html` | Reports UI | Report list, create form |
| `app/templates/visualize.html` | Visualization UI | Report details, image grid |

---

## 🎯 Key Concepts

### 1. **Separation of Concerns**
- **Routes** (routers/) → Handle HTTP requests
- **Models** (models/) → Define database schema
- **Services** (services/) → Business logic & external APIs
- **Templates** (templates/) → User interface

### 2. **Background Processing**
- Report creation is fast (just saves to DB)
- Image processing happens asynchronously
- User sees success immediately, processing happens in background

### 3. **Database Relationships**
- 1 Report → Many Inferences (1-to-Many)
- Report stores basic info
- Inference stores detailed results per image

### 4. **External Services Used**
- **Google Vision API** → Text recognition (OCR)
- **AWS S3** → Image storage
- **YOLOv8 (Ultralytics)** → Object detection
- **openpyxl** → Excel generation

### 5. **Data Flow Pipeline**
```
User Upload → Save to DB → Save Files → Background Processing:
    ├─> Run OCR (Google Vision)
    ├─> Parse Results (Extract IDs)
    ├─> Detect Objects (YOLOv8)
    ├─> Upload Images (AWS S3)
    ├─> Save Results (Database)
    └─> Cleanup (Delete temp files)
```

---

## ✅ Next Steps for Understanding

1. **Start with entry points:**
   - Read `run.py` and `app/main.py`

2. **Understand routing:**
   - Check `app/routers/reports.py` for a complete flow

3. **Learn database layer:**
   - Read `backend/database.py` and models in `backend/models/`

4. **Trace image processing:**
   - Follow `backend/services/inferences.py` for the full pipeline

5. **View the UI:**
   - Open templates in `app/templates/` to see how data is displayed

---

**Document Version:** 1.0  
**Last Updated:** December 14, 2025  
**Application:** ASRS (Automated Sorting & Recognition System)
