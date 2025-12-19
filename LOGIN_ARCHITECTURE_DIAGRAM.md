# ASRS Login System - Visual Architecture

## System Overview Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     ASRS Authentication System                             │
└────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   Browser Client     │
└──────────────────────┘
         │
         │ HTTP Requests
         │
    ┌────┴────────────────────────────────────────────┐
    │                                                   │
    ▼                                                   ▼
┌─────────────────┐                          ┌──────────────────┐
│  /login         │                          │  /reports        │
│  (GET/POST)     │                          │  /visualize      │
│                 │                          │  /upload         │
│  ✅ Public      │                          │                  │
│  No auth needed │                          │  ✅ Protected    │
│                 │                          │  Auth needed     │
└─────────────────┘                          └──────────────────┘
         │                                           │
         │                                           │
         │ Invalid credentials ◄────────────────────┤ No session
         │ OR no user_id                            │
         │ OR no session                            │
         │                                           │
         └───────────────────────────────────────────┘
                        │
                        ▼
                   Show /login


         Authentication Flow
         ───────────────────

        POST /login
        (username, password)
           │
           ▼
    ┌──────────────────────────┐
    │  FastAPI Route Handler   │
    │  /app/routers/auth_routes.py
    └──────────────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │  Authenticate User       │
    │  /app/auth/auth.py       │
    │                          │
    │  1. get_user_by_username │
    │     → Query database     │
    │                          │
    │  2. verify_password      │
    │     → Compare bcrypt     │
    └──────────────────────────┘
           │
      ┌────┴────┐
      │          │
   ✅ Valid    ❌ Invalid
      │          │
      ▼          ▼
    Store    Show Error
    session  & Reload
      │      Login Page
      │          │
      │          │
      ▼
  request.session["user"] = username
  request.session["user_id"] = user.id
      │
      ▼
  Redirect to /dashboard


    Session-Protected Route
    ──────────────────────

    GET /reports
      │
      ▼
  Check: user_id = request.session.get("user_id")
      │
      ├─ Not found?
      │  └─> Redirect to /login
      │
      ├─ Found? (e.g., user_id = 2)
      │  └─> Query database:
      │      SELECT * FROM reports
      │      WHERE user_id = 2
      │
      └─> Return ONLY user's reports


           Database Structure
           ──────────────────

    ┌─────────────────────────────────────┐
    │         app.db (SQLite)             │
    │                                     │
    │  ┌──────────────────────┐          │
    │  │  user table          │          │
    │  ├──────────────────────┤          │
    │  │ id (PRIMARY KEY)     │          │
    │  │ username (UNIQUE)    │          │
    │  │ hashed_password      │          │
    │  └──────────────────────┘          │
    │                                     │
    │  ┌──────────────────────┐          │
    │  │  reports table       │          │
    │  ├──────────────────────┤          │
    │  │ id (PRIMARY KEY)     │          │
    │  │ report_name          │          │
    │  │ createdAt            │          │
    │  │ user_id (FK) ────┐   │          │
    │  └──────────────────┼───┘          │
    │                     │              │
    │  ┌──────────────────┼──┐           │
    │  │  inferences table    │          │
    │  ├──────────────────────┤          │
    │  │ id (PRIMARY KEY)     │          │
    │  │ report_id (FK) ──────┼─┐        │
    │  │ user_id (FK) ────┐   │ │       │
    │  │ unique_id        │   │ │       │
    │  │ vin_no           │   │ │       │
    │  │ quantity         │   │ │       │
    │  │ [other fields]   │   │ │       │
    │  └────────┬─────────────┴─┘       │
    │           │                        │
    │           └─ Links back to user    │
    │                                     │
    └─────────────────────────────────────┘


    User Isolation Example
    ─────────────────────

    Database State:
    ┌─────────────────────────────────────┐
    │  user table                         │
    ├─────────────────────────────────────┤
    │ id │ username │ hashed_password     │
    ├────┼──────────┼─────────────────────┤
    │ 1  │ admin    │ $2b$12$... (hash)   │
    │ 2  │ staff1   │ $2b$12$... (hash)   │
    └─────────────────────────────────────┘

    ┌─────────────────────────────────────┐
    │  reports table                      │
    ├─────────────────────────────────────┤
    │ id │ report_name │ user_id          │
    ├────┼─────────────┼──────────────────┤
    │ 1  │ Report A    │ 1 (admin)        │
    │ 2  │ Report B    │ 2 (staff1)       │
    │ 3  │ Report C    │ 2 (staff1)       │
    │ 4  │ Report D    │ 1 (admin)        │
    └─────────────────────────────────────┘


    When admin (user_id=1) logs in:
    ┌──────────────────────────────────┐
    │  Query: SELECT * FROM reports    │
    │         WHERE user_id = 1        │
    │                                  │
    │  Results:                        │
    │  ✅ Report A (user_id=1)         │
    │  ❌ Report B (user_id=2)         │
    │  ❌ Report C (user_id=2)         │
    │  ✅ Report D (user_id=1)         │
    │                                  │
    │  Display: Report A, Report D     │
    └──────────────────────────────────┘


    When staff1 (user_id=2) logs in:
    ┌──────────────────────────────────┐
    │  Query: SELECT * FROM reports    │
    │         WHERE user_id = 2        │
    │                                  │
    │  Results:                        │
    │  ❌ Report A (user_id=1)         │
    │  ✅ Report B (user_id=2)         │
    │  ✅ Report C (user_id=2)         │
    │  ❌ Report D (user_id=1)         │
    │                                  │
    │  Display: Report B, Report C     │
    └──────────────────────────────────┘


    Request Lifecycle - With Session
    ────────────────────────────────

    1️⃣  User fills login form
        username: "admin"
        password: "admin123"
                │
                ▼
    2️⃣  POST /login
        handler receives credentials
                │
                ▼
    3️⃣  Lookup in database
        SELECT * FROM user
        WHERE username = "admin"
        → Found: User(id=1, ...)
                │
                ▼
    4️⃣  Verify password
        bcrypt.verify("admin123", hashed_password)
        → True ✅
                │
                ▼
    5️⃣  Store in session
        request.session["user"] = "admin"
        request.session["user_id"] = 1
        (Stored in browser cookie - encrypted)
                │
                ▼
    6️⃣  Redirect to /dashboard
        response.status_code = 303
        response.headers["Location"] = "/dashboard"
                │
                ▼
    7️⃣  Browser makes request:
        GET /dashboard
        Cookie: session=eyJu... (encrypted)
                │
                ▼
    8️⃣  Route handler:
        user_id = request.session.get("user_id")
        # Returns: 1
        
        Query reports for user_id=1:
        db.query(Report).filter(Report.user_id == 1)
                │
                ▼
    9️⃣  Return user's reports
        [Report A, Report D]
        Display in dashboard


    Password Security Flow
    ─────────────────────

    User Input: "admin123"
        │
        ▼
    Bcrypt Hash Function (one-way)
        │
        ├─ Input: "admin123"
        ├─ Generate salt
        ├─ Apply 12 rounds of hashing
        ├─ Result: $2b$12$R9h/cIPz0gi.URNNGU3mkfn7FqcH...
        │
        └─> Cannot be reversed ✅
        
    During Login:
        │
        ├─ User enters: "admin123"
        ├─ Get hashed password from DB:
        │  "$2b$12$R9h/cIPz0gi.URNNGU3mkfn7FqcH..."
        │
        ├─ bcrypt.verify(user_input, db_hash)
        │  ├─ Apply same function to user input
        │  ├─ Compare result with db_hash
        │  └─ If match: ✅ Correct password
        │     If no match: ❌ Wrong password
        
    Never stored as plain text ✅
    Never transmitted over network ❌
    Always compared via bcrypt ✅


    Security Checks Timeline
    ────────────────────────

    Request to /reports
            │
            ▼
    ┌─ Check 1: Session exists?
    │  ├─ session["user_id"] exists?
    │  ├─ No? → Redirect to /login
    │  └─ Yes? → Continue
    │           │
    │           ▼
    ├─ Check 2: User authorized to view report?
    │  ├─ Query: SELECT * FROM reports
    │  │          WHERE report_id = requested_id
    │  │          AND user_id = session["user_id"]
    │  ├─ Not found? → Show "Report not found"
    │  └─ Found? → Return report data
    │
    └─ Both checks passed → Display report ✅


    Logout Flow
    ──────────

    User clicks "Logout"
            │
            ▼
    GET /logout
            │
            ▼
    request.session.clear()
    (Deletes all session data)
            │
            ├─ session["user"] = removed
            ├─ session["user_id"] = removed
            │
            ▼
    Redirect to /login
            │
            ▼
    User returned to login page
    Next request to /reports:
    ├─ Check: request.session.get("user_id")
    ├─ Returns: None
    └─> Redirect to /login ✅
```

---

## Key Security Checkpoints

### 1. Login Check
```python
@router.get("/reports")
def reports_page(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/login")  # ← Security checkpoint
```

### 2. Ownership Check
```python
@router.get("/visualize")
def visualize(request: Request, report: int):
    user_id = request.session.get("user_id")
    
    # Ensure user owns this report
    selected_report = db.query(Report).filter(
        Report.id == report,
        Report.user_id == user_id  # ← Security checkpoint
    ).first()
```

### 3. Query Isolation
```python
# Instead of: SELECT * FROM reports
# Do this: SELECT * FROM reports WHERE user_id = <current_user>

query = db.query(Report).filter(Report.user_id == user_id)
```

---

## Attack Prevention

| Attack Type | Prevention | Implementation |
|------------|-----------|-----------------|
| Unauthorized Access | User ID validation | `user_id == session["user_id"]` |
| Session Hijacking | Session encryption | SessionMiddleware |
| Brute Force | Account lockout | Not implemented (TODO) |
| SQL Injection | ORM queries | SQLAlchemy protects |
| CSRF | CSRF token | StandardMiddleware |
| Password Exposure | Bcrypt hashing | One-way encryption |

---

## Implementation Checklist

- [x] User table with hashed passwords
- [x] Report table with user_id
- [x] Inference table with user_id
- [x] Login page (no signup)
- [x] Session management
- [x] Report filtering by user_id
- [x] Ownership validation
- [x] Logout functionality
- [x] Documentation

---

**Version:** 1.0  
**Last Updated:** December 16, 2025
