# Quick Start Guide - ASRS Testing

## 🚀 Quick Setup & Testing

### Step 1: Install Missing Dependencies
```bash
cd /home/ostajanpure/Desktop/ASRS-prod
pip install qrcode reportlab pillow
```

### Step 2: Start the Server
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Access the Application
Open your browser and navigate to: **http://localhost:8000**

You will be automatically redirected to `/login` page.

---

## 📋 Testing Checklist

### Phase 1: Authentication (5 minutes)

**Test Signup:**
1. Click "Create one" on login page
2. Enter username: `testuser`
3. Enter password: `TestPass123!`
4. Confirm password: `TestPass123!`
5. Click "Create Account"
✅ Should redirect to dashboard

**Test Password Validation:**
1. Go back to signup
2. Enter password less than 6 characters
3. Should show error message
✅ Should prevent submission

**Test Login:**
1. Click "Sign in" link
2. Enter username and password
3. Click "Sign In"
✅ Should redirect to dashboard

**Test Invalid Login:**
1. Enter wrong username or password
2. Click "Sign In"
✅ Should show "Invalid username or password"

**Test Logout:**
1. On dashboard, click "Logout" button
✅ Should redirect to login page

---

### Phase 2: Dashboard (3 minutes)

**Verify Dashboard Elements:**
1. Welcome message visible
2. 4 stat cards showing:
   - Total Reports
   - QR Codes Generated
   - Reports Today
   - System Status
3. Quick action buttons (4 buttons):
   - View Reports
   - Upload Images
   - Visualize Data
   - Generate QR
4. Activity chart with data
5. Logout button visible

**Test Quick Action Buttons:**
1. Click "View Reports" → Should go to `/reports` page ✅
2. Click "Upload Images" → Should go to `/upload` page ✅
3. Click "Visualize Data" → Should go to `/visualize` page ✅
4. Click "Generate QR" → Should go to `/qr` page ✅

---

### Phase 3: QR Code Generation (5 minutes)

**Navigate to QR Page:**
1. Go to Dashboard
2. Click "Generate QR" button
3. You should see the QR generation page with:
   - Single VIN form
   - Bulk VIN form
   - Input fields and buttons

**Test Single VIN QR:**
1. Enter VIN: `1HGCV41JXMN109186` (17 characters)
2. Click "Generate QR Code"
✅ Should download PDF file: `QR_1HGCV41JXMN109186.pdf`

**Test VIN Validation:**
1. Enter VIN: `123` (too short)
2. Click "Generate QR Code"
✅ Should show error: "VIN must be exactly 17 characters"

**Test Bulk QR Generation:**
1. In bulk form, enter multiple VINs:
```
1HGCV41JXMN109186
2HGCV41JXMN109187
3HGCV41JXMN109188
```
2. Click "Generate Bulk QR Codes"
✅ Should download PDF with 3 pages: `QR_Bulk_3_codes.pdf`

---

### Phase 4: Reports Page (5 minutes)

**View Reports:**
1. Click "View Reports" from dashboard or upload button
2. Should see:
   - Cards showing existing reports
   - Each card shows report name and item count
   - Search box at top
   - File upload area

**Test Report Creation:**
1. Go to `/reports` page
2. In upload form:
   - Enter Report Name: `Test Report 1`
   - Drag-drop an image file (or click to select)
   - Click submit
✅ Should show success message
✅ Should appear in reports list

**Test Search:**
1. Enter search term in search box
2. Cards should filter in real-time
✅ Only matching reports should show

**Test Delete:**
1. Click delete button on a report card
✅ Should remove from list (may ask for confirmation)

---

### Phase 5: Visualization Page (5 minutes)

**View Visualization:**
1. Click "Visualize Data" or go to `/visualize`
2. Should see:
   - Left panel: List of reports
   - Right panel: Report details and images
   - Search and date filter

**Test Report Selection:**
1. Click on a report in the list
2. Right panel should show:
   - Report details
   - Images in grid
   - Image count badge

**Test Image Modal:**
1. Click on an image in the grid
2. Should open modal/popup with:
   - Full image view
   - Close button
✅ Click close to dismiss

**Test Filters:**
1. Use search box to filter reports
2. Select a date from dropdown
3. Reports should update in real-time

---

### Phase 6: Upload & Processing (10 minutes)

**Test File Upload:**
1. Go to `/upload` page
2. Enter report name
3. Select image files (JPG, PNG)
4. Click submit
✅ Should process in background
✅ Files should appear in visualization page

---

## 🔍 Error Checking

Check terminal for any errors:
```bash
# Should see requests like:
GET /login - 200 OK
POST /login - 303 See Other (redirect to dashboard)
GET /dashboard - 200 OK
GET /reports - 200 OK
```

**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| Module not found: `qrcode` | Run: `pip install qrcode` |
| Module not found: `reportlab` | Run: `pip install reportlab` |
| Database connection error | Check MySQL connection in `.env` |
| Session not working | Verify SECRET_KEY is set |
| Images not loading | Check AWS S3 credentials |

---

## 📊 Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| Login | ✅ Complete | Session-based auth working |
| Signup | ✅ Complete | Password validation enabled |
| Dashboard | ✅ Complete | Stats hardcoded, can be enhanced |
| QR Single | ✅ Complete | Generates PDF with QR code |
| QR Bulk | ✅ Complete | Multiple QR codes per PDF |
| Reports | ✅ Complete | Create, view, delete working |
| Visualization | ✅ Complete | Image viewer with modal |
| Upload | ✅ Complete | Background processing enabled |

---

## 🎯 Success Criteria

Your ASRS implementation is successful if:
- ✅ Can create account and login
- ✅ Dashboard loads with stats and charts
- ✅ Can generate single and bulk QR codes (PDFs)
- ✅ Can create and view reports
- ✅ Can upload images and see them in visualization
- ✅ All pages are responsive and styled properly
- ✅ No console errors or 500 errors

---

## 📝 Testing Notes

**Test Date:** December 11, 2025

**Test Environment:**
- Python 3.14
- FastAPI with Uvicorn
- SQLModel with MySQL
- Modern browsers (Chrome, Firefox, Safari)

**Test User:**
- Username: `testuser`
- Password: `TestPass123!`

---

## 🚀 Ready for Production?

Before deploying to production:
- [ ] Change SECRET_KEY to secure random value
- [ ] Set up proper database backups
- [ ] Configure HTTPS/SSL
- [ ] Set up email notifications
- [ ] Configure AWS S3 properly
- [ ] Set up monitoring and logging
- [ ] Perform security audit
- [ ] Load testing

---

**Happy Testing! 🎉**

For any issues, check the terminal output for error messages and stack traces.
