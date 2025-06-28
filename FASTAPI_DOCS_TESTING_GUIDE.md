# Testing KASA in FastAPI Documentation (Swagger UI)

## 🌐 Access the Interactive Docs

1. **Start the server**:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
   ```

2. **Open FastAPI Docs**:
   - Go to: **http://127.0.0.1:8080/docs**
   - This opens the interactive Swagger UI

## 📋 Step-by-Step Testing Guide

### Step 1: Check System Status

1. **Test `/` (Root Endpoint)**
   - Click on the **GET /** endpoint
   - Click **"Try it out"**
   - Click **"Execute"**
   - Should show system overview with stats

2. **Test `/health` (Health Check)**
   - Click on **GET /health**
   - Click **"Try it out"** → **"Execute"**
   - Should return `{"status": "healthy"}`

### Step 2: Upload Users via CSV

1. **Find the `/upload-users` endpoint**
   - Look for **POST /upload-users**
   - Click to expand it

2. **Prepare CSV content**:
   ```csv
   name,phone,location
   John Doe,+254711123456,Nairobi CBD
   Jane Smith,+254712234567,Westlands
   Bob Johnson,+254720345678,Kilimani
   Alice Brown,+254733456789,Eastlands
   ```

3. **Upload the CSV**:
   - Click **"Try it out"**
   - Click **"Choose File"** or the file upload area
   - Create a text file with the CSV content above
   - Save it as `test_users.csv`
   - Upload the file
   - Click **"Execute"**

4. **Expected Response**:
   ```json
   {
     "message": "CSV upload completed",
     "imported_count": 4,
     "error_count": 0,
     "duplicate_count": 0,
     "total_users_now": 4,
     "imported_users": [...]
   }
   ```

### Step 3: Query Users

1. **Get All Users**
   - Find **GET /users**
   - Click **"Try it out"** → **"Execute"**
   - Should show all uploaded users with location summary

2. **Get Users by Location**
   - Find **GET /users/location/{location}**
   - Click **"Try it out"**
   - Enter location: `Westlands`
   - Click **"Execute"**
   - Should show only users in Westlands

### Step 4: Test Location Alerts

1. **Find `/send-location-alert`**
   - Look for **POST /send-location-alert**
   - Click to expand

2. **Send Location Alert**:
   - Click **"Try it out"**
   - Fill in the form:
     - **location**: `Westlands`
     - **message**: `Traffic jam on Waiyaki Way. Use alternative routes.`
   - Click **"Execute"**

3. **Expected Response**:
   ```json
   {
     "status": "success",
     "message": "Alert sent to 1 users in Westlands",
     "sent_count": 1,
     "location": "Westlands",
     "recipients": ["+254712234567"]
   }
   ```

### Step 5: Test USSD Endpoint

1. **Find `/ussd` endpoint**
   - Look for **POST /ussd**
   - This simulates USSD requests

2. **Test Main Menu**:
   - Click **"Try it out"**
   - Fill in:
     - **sessionId**: `ATUid_test_123`
     - **serviceCode**: `*123#`
     - **phoneNumber**: `+254799123456`
     - **text**: `` (leave empty for main menu)
   - Click **"Execute"**

3. **Expected Response**:
   ```
   CON Welcome to KASA - Local Alert System
   1. Send Emergency Alert
   2. Register User
   3. View System Status
   4. Help
   0. Exit
   ```

### Step 6: Test USSD Registration Flow

1. **Start Registration** (Option 2):
   - **sessionId**: `ATUid_reg_123`
   - **serviceCode**: `*123#`
   - **phoneNumber**: `+254766123456`
   - **text**: `2`
   - Expected: "CON Enter your full name:"

2. **Enter Name**:
   - Same session details but **text**: `Michael Test`
   - Expected: "CON Hello Michael Test! Enter your location/area:"

3. **Enter Location**:
   - Same session, **text**: `Parklands`
   - Expected: Confirmation menu

4. **Confirm Registration**:
   - Same session, **text**: `1`
   - Expected: "END Registration successful!"

### Step 7: Test Emergency Alert

1. **Emergency Flow**:
   - **sessionId**: `ATUid_emergency_123`
   - **phoneNumber**: `+254711123456` (registered user)
   - **text**: `1*1*1` (Emergency > Fire > Confirm)

2. **Expected Response**:
   ```
   END Fire Emergency alert sent!
   Reference: EMR-12345678
   Location: 📍Nairobi Central Business District | 🏢Near Kenyatta Avenue
   ✓ 3 local users notified
   Stay safe!
   ```

### Step 8: View Emergency Reports

1. **Get Emergency Reports**:
   - Find **GET /emergency-reports**
   - Click **"Try it out"** → **"Execute"**
   - Shows all emergency alerts with location details

## 🎯 Testing Scenarios

### Scenario A: Complete User Journey
1. Upload users via CSV ✅
2. Register new user via USSD ✅
3. Send location alert ✅
4. Generate emergency alert ✅
5. View all reports ✅

### Scenario B: Error Testing
1. **Invalid CSV**: Upload CSV with wrong headers
2. **Duplicate Registration**: Try registering same phone number
3. **Invalid Location**: Send alert to non-existent location
4. **Invalid Phone**: Use malformed phone number

### Scenario C: USSD Flow Testing
1. **Navigation**: Test all menu options (1, 2, 3, 4, 0)
2. **Registration Cancellation**: Start registration, then cancel
3. **Session Reset**: Test session cleanup
4. **Invalid Inputs**: Test invalid menu selections

## 📊 Expected Test Results

### CSV Upload Success:
```json
{
  "message": "CSV upload completed",
  "imported_count": 4,
  "error_count": 0,
  "duplicate_count": 0,
  "total_users_now": 4
}
```

### Location Alert Success:
```json
{
  "status": "success",
  "message": "Alert sent to 1 users in Westlands",
  "sent_count": 1,
  "location": "Westlands"
}
```

### USSD Registration Success:
```
END Registration successful!
Name: Michael Test
Location: Parklands
Phone: +254766123456
You can now receive location alerts!
```

## 🔍 Debugging Tips

1. **Check Server Logs**: Monitor the terminal running the server for detailed logs
2. **Response Codes**: 
   - 200 = Success
   - 400 = Bad Request (check your input)
   - 500 = Server Error (check logs)
3. **JSON Validation**: Make sure JSON inputs are properly formatted
4. **Phone Numbers**: Always use international format (+254...)

## 📱 FastAPI Docs Features

- **Try it out**: Interactive testing
- **Request/Response Examples**: See expected formats
- **Schema Documentation**: View data models
- **Authentication**: Test with API keys (if enabled)
- **Download OpenAPI**: Export API specification

## 🚀 Advanced Testing

### Custom Phone Numbers
Use these for location testing:
- `+254711123456` → Nairobi CBD
- `+254712234567` → Westlands  
- `+254720345678` → Kilimani

### Error Cases to Test
1. Empty CSV file
2. CSV with missing headers
3. Invalid phone number format
4. Long message (>160 characters)
5. Special characters in names/locations

## 📋 Testing Checklist

- [ ] System status endpoints work
- [ ] CSV upload accepts valid files
- [ ] CSV upload rejects invalid files
- [ ] User queries return correct data
- [ ] Location alerts send to correct users
- [ ] USSD main menu displays correctly
- [ ] USSD registration flow completes
- [ ] Emergency alerts include location
- [ ] Duplicate detection works
- [ ] Error handling is graceful

## 🎉 Success Indicators

✅ **All endpoints return 200 status codes**
✅ **Users are successfully imported and stored**
✅ **Location alerts reach the correct recipients**
✅ **USSD flows complete without errors**
✅ **Emergency alerts include location context**
✅ **System handles errors gracefully**

The FastAPI docs provide a complete testing environment for all KASA features!
