# ASRS User Management & Authentication Guide

## Overview

The ASRS application now implements a **dedicated user authentication system** where:
- ✅ Only **pre-assigned users** can login (no self-signup)
- ✅ Each user sees **only their own reports**
- ✅ Each report is **linked to a specific user** via `user_id`
- ✅ All user credentials are **stored in `app.db`** (SQLite)

---

## 1. Database Storage - Does Login Data Get Stored?

### ✅ **YES - Logins are stored in `app.db`**

**Location:** `/home/ostajanpure/Desktop/ASRS-prod/app.db` (SQLite database)

**User Table Schema:**
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL
)
```

**What Gets Stored:**
- ✅ Username (plain text)
- ✅ Password (hashed with bcrypt - never plain text)
- ✅ User ID (auto-incrementing integer)

**Password Security:**
- Passwords are hashed using **bcrypt** algorithm
- Never stored in plain text
- Cannot be reversed (one-way encryption)

---

## 2. User-Dedicated Reports System

### How Reports Get Linked to Users

**Report Model:**
```python
class Report(Base):
    id = Column(Integer, primary_key=True)
    report_name = Column(String(25))
    createdAt = Column(Date)
    user_id = Column(Integer)  # NEW: Links to User.id
```

**Inference Model:**
```python
class Inference(Base):
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer)
    user_id = Column(Integer)  # NEW: Links to User.id
    unique_id = Column(String(7))
    vin_no = Column(String(25))
    # ... other fields
```

### Report Access Flow

```
User Logs In
    ↓
Session stores: user_id
    ↓
User creates report
    ↓
report.user_id = session.user_id  [Linked at creation]
    ↓
User views reports
    ↓
Query: SELECT * FROM reports WHERE user_id = session.user_id
    ↓
Only that user's reports shown
```

---

## 3. User Management - Creating & Assigning Users

### Method 1: Using create_db.py (Recommended)

**File:** `/home/ostajanpure/Desktop/ASRS-prod/create_db.py`

**To add more users, edit the `users` list:**

```python
users = [
    {"username": "admin", "password": "admin123"},
    {"username": "staff1", "password": "staff123"},
    {"username": "staff2", "password": "staff456"},
    {"username": "john_smith", "password": "john@2025"},  # ADD NEW USER HERE
    {"username": "jane_doe", "password": "jane@2025"},    # ADD NEW USER HERE
]
```

**Then run:**
```bash
python create_db.py
```

**Output:**
```
✅ Created user: admin (ID: 1)
✅ Created user: staff1 (ID: 2)
✅ Created user: staff2 (ID: 3)
✅ Created user: john_smith (ID: 4)
✅ Created user: jane_doe (ID: 5)
⚠️  User 'admin' may already exist: [if user already exists]
```

### Method 2: Manual Database Insert (Advanced)

Using SQLite command line:

```bash
sqlite3 app.db
```

```sql
INSERT INTO user (username, hashed_password) 
VALUES ('new_user', 'hashed_password_here');
```

> ⚠️ **Note:** Hashed password must be generated with bcrypt. Use Method 1 instead.

---

## 4. Login System (No Signup)

### Changes Made

**Signup Page:** ❌ **REMOVED**
**Signup Route:** ❌ **REMOVED**
**Login Page:** ✅ **ONLY LOGIN AVAILABLE**

### Login Flow

```
1. User navigates to http://localhost:8000/login
2. User enters USERNAME (e.g., "admin")
3. User enters PASSWORD (e.g., "admin123")
4. Click "Sign In"
5. Backend verifies:
   - Username exists in database
   - Password matches (bcrypt verification)
6. If valid:
   - Session stores: user_id
   - Redirect to /dashboard
7. If invalid:
   - Show error: "Invalid username or password"
   - Stay on login page
```

### Default Test Users

These are pre-configured in the database:

| Username | Password | ID |
|----------|----------|-----|
| admin | admin123 | 1 |
| staff1 | staff123 | 2 |
| staff2 | staff456 | 3 |

---

## 5. Session Management

### Session Storage

**Session Middleware:** Starlette SessionMiddleware

**Session Data Stored:**
```python
request.session["user"]       # Username
request.session["user_id"]    # User ID (integer)
```

**Duration:** Session lasts until browser closes or user logs out

### How Session Works

```python
# During login
request.session["user"] = username
request.session["user_id"] = user.id

# Later in requests
user_id = request.session.get("user_id")
if not user_id:
    redirect_to_login()
else:
    # Show user's reports
```

---

## 6. Report Filtering by User

### Reports Page (`/reports`)

**Before:** Shows all reports from all users
**Now:** Shows only logged-in user's reports

```python
@router.get("/reports")
def reports_page(request: Request):
    user_id = request.session.get("user_id")
    
    query = db.query(Report).filter(
        Report.user_id == user_id  # FILTER BY USER
    ).order_by(Report.createdAt.desc())
    
    reports = query.all()
    # Only this user's reports returned
```

### Visualize Page (`/visualize`)

**Before:** All reports accessible to anyone who knew the report ID
**Now:** Only report owner can view

```python
# When viewing report details
selected_report = db.query(Report).filter(
    Report.id == selected_report_id,
    Report.user_id == user_id  # ENSURE OWNER MATCHES
).first()
```

### Upload Page (`/upload`)

**File:** `/app/routers/upload.py`

New reports are created with:
```python
user_id = request.session.get("user_id")
create_report(report_name, user_id)  # NEW: Pass user_id
```

---

## 7. Security Features

### ✅ **1. Login Required**
- All report pages redirect to `/login` if user not authenticated
- Session must exist to access `/reports`, `/visualize`, `/upload`

### ✅ **2. User Isolation**
- Each user only sees their own reports
- Cannot access other users' reports via URL
- Database queries filtered by `user_id`

### ✅ **3. Password Security**
- Passwords hashed with bcrypt (one-way)
- Original password never stored
- Cannot reverse-engineer password

### ✅ **4. No Signup**
- Only admin can create users
- Users cannot self-register
- Prevents unauthorized account creation

### ✅ **5. No Self-Service Account Recovery**
- Admins must create accounts
- No password reset functionality
- Admins must reset forgotten passwords by creating new account

---

## 8. Logout System

### How Logout Works

```python
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")
```

**Action:** Clears all session data

**Result:** User must login again to access reports

---

## 9. Admin User Management Tasks

### Task 1: Create New User

**Step 1:** Edit `/create_db.py`
```python
users = [
    {"username": "admin", "password": "admin123"},
    {"username": "jane_doe", "password": "jane2025!"},  # NEW
]
```

**Step 2:** Run the script
```bash
python create_db.py
```

**Step 3:** Give credentials to user

---

### Task 2: Delete User

**Step 1:** Delete via SQLite
```bash
sqlite3 app.db
DELETE FROM user WHERE username = 'jane_doe';
```

**Step 2:** Optionally delete their reports
```sql
DELETE FROM reports WHERE user_id = 3;
DELETE FROM inferences WHERE user_id = 3;
```

---

### Task 3: Reset User Password

**Step 1:** Delete old user
```bash
sqlite3 app.db
DELETE FROM user WHERE username = 'jane_doe';
```

**Step 2:** Add user again with `create_db.py`

---

## 10. Database Queries Reference

### View All Users
```bash
sqlite3 app.db
SELECT * FROM user;
```

### View User's Reports
```bash
SELECT * FROM reports WHERE user_id = 2;
```

### View User's Inferences
```bash
SELECT * FROM inferences WHERE user_id = 2;
```

### Count Reports by User
```bash
SELECT user_id, COUNT(*) as report_count FROM reports GROUP BY user_id;
```

### Delete All Reports for User
```bash
DELETE FROM inferences WHERE user_id = 2;
DELETE FROM reports WHERE user_id = 2;
```

---

## 11. Testing the System

### Test 1: Login with Correct Credentials

```
URL: http://localhost:8000/login
Username: admin
Password: admin123
Expected: Redirects to /dashboard ✅
```

### Test 2: Login with Wrong Password

```
URL: http://localhost:8000/login
Username: admin
Password: wrongpassword
Expected: Error message shown ✅
```

### Test 3: Create Report and See Only Your Reports

```
1. Login as admin (user_id=1)
2. Create Report A
3. Login as staff1 (user_id=2)
4. /reports should show ONLY Report A if created by staff1
5. Admin should NOT see staff1's reports ✅
```

### Test 4: Try to Access Another User's Report

```
1. Login as admin (user_id=1)
2. Get admin's report ID (e.g., ID=5)
3. Logout
4. Login as staff1 (user_id=2)
5. Try to access /visualize?report=5
6. Expected: Report details not shown (404 or no data) ✅
```

### Test 5: Logout

```
1. Click logout button
2. Expected: Redirects to /login
3. Try to access /reports
4. Expected: Redirects to /login ✅
```

---

## 12. File Changes Summary

### Files Modified:

| File | Change | Impact |
|------|--------|--------|
| `app/templates/login.html` | Removed signup link | Users can't self-register |
| `app/routers/auth_routes.py` | Removed signup routes | No signup page available |
| `backend/models/report.py` | Added `user_id` column | Reports linked to users |
| `backend/models/inference.py` | Added `user_id` column | Inferences linked to users |
| `backend/services/data_manager.py` | Updated `create_report()` | Accepts `user_id` parameter |
| `backend/services/inferences.py` | Updated `get_inferences()` | Accepts `user_id` parameter |
| `app/routers/reports.py` | Added user filtering | Show only user's reports |
| `app/routers/visualize.py` | Added user filtering | Show only user's reports |
| `create_db.py` | Enhanced user creation | Add multiple pre-assigned users |

---

## 13. Troubleshooting

### Issue: "Invalid username or password"

**Possible Causes:**
1. Username doesn't exist in database
2. Password is incorrect
3. Database not initialized

**Solution:**
```bash
# Check users exist
sqlite3 app.db
SELECT * FROM user;

# If empty, run:
python create_db.py
```

---

### Issue: User sees all reports, not just their own

**Cause:** Database migrations not applied

**Solution:**
```bash
# Check database schema
sqlite3 app.db
.schema reports
.schema inferences

# Should show user_id column in both tables
```

---

### Issue: Excel export "Report not found"

**Cause:** User doesn't own the report

**Solution:** Only report owner can download Excel. Check:
```bash
sqlite3 app.db
SELECT * FROM reports WHERE id = <report_id>;
# Should show same user_id as logged-in user
```

---

## 14. API Reference

### Authentication Endpoints

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---|
| `/login` | GET | Show login page | No |
| `/login` | POST | Process login | No |
| `/logout` | GET | Clear session | Yes |
| `/dashboard` | GET | Show dashboard | Yes |

### Report Endpoints (All Require Auth)

| Endpoint | Method | Filter |
|----------|--------|--------|
| `/reports` | GET | `user_id == session.user_id` |
| `/reports/create` | POST | Creates with `user_id` |
| `/visualize` | GET | `user_id == session.user_id` |
| `/api/report/{id}/details` | GET | `user_id == session.user_id` |
| `/api/report/{id}/export/excel` | GET | `user_id == session.user_id` |

---

## 15. Summary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ASRS Authentication                      │
└─────────────────────────────────────────────────────────────┘

                    app.db (SQLite)
                    ├─ user table
                    │  ├─ id (auto)
                    │  ├─ username
                    │  └─ hashed_password
                    │
                    ├─ reports table
                    │  ├─ id
                    │  ├─ report_name
                    │  ├─ createdAt
                    │  └─ user_id ← LINKS TO user.id
                    │
                    └─ inferences table
                       ├─ id
                       ├─ report_id
                       ├─ user_id ← LINKS TO user.id
                       └─ [other fields]


         User Login Flow
         ─────────────────

Login Page ──┐
             │
            POST /login (username, password)
             │
             ├─ Hash password
             ├─ Query: SELECT * FROM user WHERE username = ?
             ├─ Verify hash matches
             │
             ├─ Valid? → Set session["user_id"]
             │           Redirect /dashboard ✅
             │
             └─ Invalid? → Show error ❌
               

         Report Access Control
         ──────────────────────

/reports ──┐
/visualize │
/upload   ─┤
           │
           ├─ Get user_id from session
           ├─ Check session exists (if not → /login)
           │
           ├─ Query reports with WHERE user_id = session.user_id
           │
           └─ Return only matching reports ✅
```

---

**Version:** 1.0  
**Last Updated:** December 16, 2025  
**For:** ASRS Development Team
