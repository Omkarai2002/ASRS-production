# Dynamic Settings & Visualization System - Implementation Guide

**Date:** December 22, 2025  
**Status:** ✅ Complete  
**Version:** 1.0

---

## Overview

A comprehensive settings system has been implemented to allow users to customize the visualization of their stored items with dynamic grid layouts and intelligent level naming.

### Key Features:
- 🎚️ **Dynamic Grid Configuration** - Set images per row (1-20)
- 🏢 **Level Naming System** - Customizable prefixes (L, Level, Storage, Rack, etc.)
- 👁️ **Display Options** - Toggle image metadata and level information
- 📊 **Real-time Preview** - Live preview of layout and naming before saving
- 💾 **Persistent Storage** - Settings saved per user in database

---

## Architecture

### Database Models

#### UserSettings Model (`backend/models/user_settings.py`)
```python
class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id: Integer (Primary Key)
    user_id: Integer (Unique, Foreign Key to User)
    
    # Visualization Settings
    images_per_row: Integer (default: 8, range: 1-20)
    level_prefix: String (default: "L", max 50 chars)
    
    # Display Options
    image_size: String (small/medium/large)
    show_image_info: Boolean (show metadata)
    show_level_info: Boolean (show level info)
    
    # Timestamps
    createdAt: DateTime
    updatedAt: DateTime
```

---

## Components

### 1. Settings Page Template (`app/templates/settings.html`)

**URL:** `/settings`

**Features:**
- Two-column responsive layout
- Visualization settings card
  - Images per row input (1-20)
  - Level prefix input with real-time preview
  - Image size selector (small/medium/large)
- Display options card
  - Checkboxes for metadata and level display
  - Grid layout preview
  - Level naming preview
- Real-time JavaScript previews
  - Updates level tags as you type
  - Updates grid layout as you adjust images per row

**Preview Section:**
```
Level Naming Preview:    L1-1  L1-2  L2-1  L2-2
Grid Layout Preview:     [8 boxes arranged in 1 row]
```

### 2. Settings Backend Route (`app/routers/settings.py`)

**GET /settings**
- Displays settings page
- Retrieves user's current settings from database
- Auto-creates default settings if first-time user

**POST /settings/update**
- Validates all input (numbers, strings)
- Ensures `images_per_row` is between 1-20
- Saves settings to database
- Redirects with success/error message

**Error Handling:**
- Invalid number input → defaults to 8
- Empty prefix → defaults to "L"
- SQL errors → user-friendly error message

### 3. Visualization Updates (`app/routers/visualize.py`)

**Changes:**
1. Fetches user settings on page load
2. Creates default settings if not exists
3. **Level Calculation Algorithm:**
   ```python
   for each image (index 0 to N):
       level_number = (index // images_per_row) + 1
       position_in_level = (index % images_per_row) + 1
       level_name = f"{level_prefix}{level_number}-{position_in_level}"
   ```

**Example with L prefix and 8 images per row:**
```
Image 0: L1-1   Image 1: L1-2   Image 2: L1-3   Image 3: L1-4
Image 4: L1-5   Image 5: L1-6   Image 6: L1-7   Image 7: L1-8
Image 8: L2-1   Image 9: L2-2   Image 10: L2-3  ...
```

**Alternative prefix "Rack":**
```
Image 0: Rack1-1   Image 1: Rack1-2   ...   Image 8: Rack2-1   ...
```

### 4. Visualization Template Updates (`app/templates/visualize.html`)

**CSS Changes:**
- Grid now respects user settings
- Dynamic grid-template-columns
- Added level badge styling (absolute positioned)
- Added level info display section

**HTML Enhancements:**
- Level badge shown in top-left of each image card
- Level info section at bottom: "Level X • Position Y"
- Level information visible even without clicking

**Grid Layout:**
```
grid-template-columns: repeat(8, 1fr);  /* Changes based on user setting */
gap: 20px;
```

---

## Level Naming System Examples

### Example 1: Default (L prefix, 8 per row)
| Position | Name | Position | Name | Position | Name | Position | Name |
|----------|------|----------|------|----------|------|----------|------|
| 1 | L1-1 | 3 | L1-3 | 5 | L1-5 | 7 | L1-7 |
| 2 | L1-2 | 4 | L1-4 | 6 | L1-6 | 8 | L1-8 |
| 9 | L2-1 | 11 | L2-3 | 13 | L2-5 | 15 | L2-7 |

### Example 2: Storage Racks (Storage prefix, 6 per row)
| Position | Name | Position | Name | Position | Name |
|----------|------|----------|------|----------|------|
| 1 | Storage1-1 | 3 | Storage1-3 | 5 | Storage1-5 |
| 2 | Storage1-2 | 4 | Storage1-4 | 6 | Storage1-6 |
| 7 | Storage2-1 | 9 | Storage2-3 | 11 | Storage2-5 |

### Example 3: Warehouse Aisles (Aisle prefix, 10 per row)
```
Aisle1-1, Aisle1-2, Aisle1-3, ..., Aisle1-10,
Aisle2-1, Aisle2-2, ..., Aisle3-1, ...
```

---

## User Flow

### Setting Configuration
```
1. User clicks "Settings" in navigation
   ↓
2. Lands on /settings page
   ↓
3. Sees current settings (or defaults)
   ↓
4. Adjusts preferences:
   - Slides "Images Per Row" from 8 to 6
   - Changes "Level Prefix" from "L" to "Rack"
   - Toggles checkboxes for display options
   ↓
5. Watches real-time previews update
   ↓
6. Clicks "Save Settings"
   ↓
7. Settings saved to database
   ↓
8. Redirected with success message
```

### Visualization with Settings
```
1. User navigates to /visualize
   ↓
2. Backend fetches user's settings (6 images per row, "Rack" prefix)
   ↓
3. User selects a report with 15 images
   ↓
4. Images rendered in dynamic grid:
   - Row 1: Rack1-1, Rack1-2, Rack1-3, Rack1-4, Rack1-5, Rack1-6
   - Row 2: Rack2-1, Rack2-2, ... Rack2-6
   - Row 3: Rack3-1, Rack3-2, Rack3-3
   ↓
5. Each image card shows:
   - Level badge: "Rack1-1" (top-left)
   - Image thumbnail
   - Metadata (ID, VIN, Qty, Status)
   - Level info: "Level 1 • Position 1"
```

---

## Database Integration

### User Settings Storage
```sql
-- Create table
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    images_per_row INTEGER DEFAULT 8,
    level_prefix VARCHAR(50) DEFAULT 'L',
    image_size VARCHAR(50) DEFAULT 'medium',
    show_image_info BOOLEAN DEFAULT TRUE,
    show_level_info BOOLEAN DEFAULT TRUE,
    createdAt DATETIME,
    updatedAt DATETIME
);
```

### Query Flow
```
GET /visualize
→ Fetch UserSettings where user_id = session.user_id
→ If not found, create with defaults
→ Query Reports and Inferences
→ Calculate levels using settings
→ Render template with data
```

---

## Navigation Updates

### base.html Changes
```html
<!-- Before -->
<li><a href="/dashboard" class="nav-link">Dashboard</a></li>
<li><a href="/reports" class="nav-link">Reports</a></li>
<li><a href="/visualize" class="nav-link">Visualize</a></li>
<li><a href="/qr" class="nav-link">QR Generation</a></li>

<!-- After -->
<li><a href="/dashboard" class="nav-link">Dashboard</a></li>
<li><a href="/reports" class="nav-link">Reports</a></li>
<li><a href="/visualize" class="nav-link">Visualize</a></li>
<li><a href="/qr" class="nav-link">QR Generation</a></li>
<li><a href="/settings" class="nav-link">Settings</a></li>  <!-- NEW -->
```

---

## Testing Scenarios

### Test 1: Default Settings
```
Steps:
1. Create new user
2. Navigate to /visualize
3. Load any report

Expected:
- Grid shows 8 images per row
- Level names: L1-1, L1-2, ..., L1-8, L2-1, ...
- All checkboxes enabled (metadata visible)
```

### Test 2: Custom Settings
```
Steps:
1. Go to /settings
2. Set images_per_row = 4
3. Set level_prefix = "Storage"
4. Uncheck "Show Image Metadata"
5. Save
6. Go to /visualize
7. Load report with 12 images

Expected:
- Grid shows 4 images per row (3 rows)
- Level names: Storage1-1, Storage1-2, Storage1-3, Storage1-4, Storage2-1, ...
- Image metadata hidden
- Level info still visible
```

### Test 3: Settings Persistence
```
Steps:
1. User A sets: 6 images per row, "Rack" prefix
2. User A logs out
3. User B logs in
4. User B goes to /visualize

Expected:
- User B sees default settings (8 per row, "L" prefix)
- User B's settings are independent

5. User A logs back in
6. User A goes to /visualize

Expected:
- User A sees their saved settings (6 per row, "Rack" prefix)
```

### Test 4: Level Badge Display
```
Steps:
1. Go to /settings with 5 images per row
2. Go to /visualize
3. Load report with images

Expected:
- Each card shows colored badge (top-left)
- Badge text: Level prefix + level + dash + position
- "Level X • Position Y" shown at bottom
- Badges positioned absolutely, never covered
```

---

## File Changes Summary

### New Files Created
```
✅ /app/routers/settings.py          (Backend settings route)
✅ /app/templates/settings.html      (Settings page UI)
```

### Modified Files
```
✅ /backend/models/user_settings.py  (Model definition)
✅ /app/main.py                      (Router registration)
✅ /app/templates/base.html          (Navigation link added)
✅ /app/routers/visualize.py         (Level calculation logic)
✅ /app/templates/visualize.html     (UI updates for levels)
```

### No Changes to
```
- Authentication system
- Report management
- Database core structure (only added user_settings table)
- User isolation logic
```

---

## API Endpoints

### GET /settings
- Displays settings form
- Requires authentication
- Returns: settings.html with user's settings

### POST /settings/update
- Updates user settings
- Form parameters:
  - `images_per_row` (integer, 1-20)
  - `level_prefix` (string, max 50)
  - `image_size` (select: small/medium/large)
  - `show_image_info` (checkbox)
  - `show_level_info` (checkbox)
- Returns: Redirect to /settings with message

### GET /api/report/{report_id}/details
- **Modified:** Now includes level information
- Response includes:
  ```json
  {
    "inferences": [
      {
        "id": 1,
        "unique_id": "ABC1234",
        "level_name": "L1-1",
        "level_number": 1,
        "position_in_level": 1,
        ...
      }
    ]
  }
  ```

---

## Performance Considerations

### Level Calculation
- **Time Complexity:** O(n) where n = number of images
- **Formula:** Simple integer division, no database queries
- **Cache:** None needed (calculation is lightweight)

### Database Queries
- Single query for UserSettings (indexed by user_id)
- No additional queries for level calculation
- **Query Optimization:** user_id is unique indexed

### Frontend Performance
- Real-time preview uses vanilla JavaScript
- No external dependencies beyond Chart.js (already used)
- Grid layout uses CSS Grid (native, no library needed)

---

## Future Enhancements

### Potential Features
1. **Batch Settings** - Apply settings to multiple reports
2. **Custom Color Schemes** - User-defined colors for level badges
3. **Export Configuration** - Save/load settings as presets
4. **Settings History** - Track changes over time
5. **Team Settings** - Share settings across team members
6. **Print Layout** - Optimize grid for printing

### API Extensions
- GET /api/settings/presets - Fetch preset configurations
- POST /api/settings/export - Export current settings
- POST /api/settings/import - Import saved settings

---

## Troubleshooting

### Issue: Settings not saving
**Solution:**
1. Check if user is logged in (session.user_id exists)
2. Verify database connection
3. Check browser console for form submission errors

### Issue: Levels not showing in visualization
**Solution:**
1. Verify UserSettings table exists and has data
2. Check if images_per_row value is valid (1-20)
3. Ensure report has images (inferences with data)

### Issue: Grid shows only 1 image per row
**Solution:**
1. Go to /settings
2. Check if images_per_row is set to 1
3. Increase value and save

### Issue: Level names incorrect
**Solution:**
1. Go to /settings
2. Verify level_prefix is set correctly
3. Check calculation: Position = (image_index % images_per_row) + 1

---

## Code Examples

### Creating User Settings (Backend)
```python
from backend.models.user_settings import UserSettings
from backend.database import SessionLocal

db = SessionLocal()
user_settings = UserSettings(
    user_id=1,
    images_per_row=8,
    level_prefix="L",
    image_size="medium",
    show_image_info=True,
    show_level_info=True
)
db.add(user_settings)
db.commit()
```

### Level Calculation (Python)
```python
images_per_row = 8
level_prefix = "L"

for idx in range(20):
    level_number = (idx // images_per_row) + 1
    position_in_level = (idx % images_per_row) + 1
    level_name = f"{level_prefix}{level_number}-{position_in_level}"
    print(f"Image {idx}: {level_name}")
```

### CSS Grid with Dynamic Columns
```css
.images-grid {
    display: grid;
    grid-template-columns: repeat(var(--images-per-row), 1fr);
    gap: 20px;
}
```

```javascript
// Set CSS variable for dynamic grid
const gridCount = userSettings.images_per_row;
document.documentElement.style.setProperty('--images-per-row', gridCount);
```

---

## Security Considerations

### Input Validation
- ✅ User can only modify their own settings
- ✅ Number range validation (1-20)
- ✅ String length validation (max 50 chars)
- ✅ User_id from session (not user input)

### Database Security
- ✅ user_id is unique indexed (no duplicate settings)
- ✅ Timestamps auto-generated (not user-provided)
- ✅ Proper error messages (no SQL revealed)

### Access Control
- ✅ Both /settings and API endpoints require authentication
- ✅ Users can only see/modify their own settings
- ✅ Cross-user settings access prevented

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-22 | Initial implementation with dynamic grid and level naming |

---

**Implementation Complete!** ✅

All components are functional and ready for testing. Users can now customize their visualization experience through the Settings page.
