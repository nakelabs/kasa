# KASA User Management & Registration Features

## Overview

The KASA (Local Alert & Notification System) has been enhanced with comprehensive user management capabilities including:

- **USSD-based User Registration**: Multi-step registration flow via USSD menu
- **CSV Bulk Import**: Admin endpoint to upload users via CSV file
- **Location-based User Management**: Query and alert users by location
- **Session State Management**: Proper USSD session handling for multi-step flows
- **Helper Functions**: Utility functions for user lookup and location-based operations

## New Features

### 1. User Registration via USSD

Users can now register directly through the USSD menu:

```
*123# → 2 (Register User) → Enter Name → Enter Location → Confirm
```

**Flow Example:**
1. User dials `*123#`
2. Selects "2. Register User"
3. Enters full name when prompted
4. Enters location/area
5. Confirms registration

**Features:**
- ✅ Duplicate registration detection
- ✅ Session state management across steps
- ✅ Input validation
- ✅ Confirmation step
- ✅ Error handling

### 2. CSV User Upload (Admin Feature)

Bulk import users via CSV file upload:

**Endpoint:** `POST /upload-users`

**CSV Format:**
```csv
name,phone,location
John Doe,+254711123456,Nairobi CBD
Jane Smith,+254712234567,Westlands
Bob Johnson,+254720345678,Kilimani
```

**Features:**
- ✅ Header validation
- ✅ Phone number format validation
- ✅ Duplicate detection
- ✅ Error reporting per row
- ✅ Batch processing summary

### 3. Location-based User Management

**Get Users by Location:**
```http
GET /users/location/{location}
```

**Send Alert to Location:**
```http
POST /send-location-alert
Content-Type: application/x-www-form-urlencoded

location=Westlands&message=Traffic alert on Waiyaki Way
```

### 4. Helper Functions

```python
# Get users in a specific location
users = get_users_by_location("Westlands")

# Send alert to all users in a location
result = send_alert_to_location("Westlands", "Emergency alert message")

# Register a new user
user = register_user("+254711123456", "John Doe", "Nairobi CBD")

# Get user by phone number
user = get_user_by_phone("+254711123456")
```

## API Endpoints

### User Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-users` | Upload CSV file to bulk import users |
| `GET` | `/users` | Get all registered users |
| `GET` | `/users/location/{location}` | Get users in a specific location |
| `POST` | `/send-location-alert` | Send alert to all users in a location |

### Enhanced USSD Menu

```
Welcome to KASA - Local Alert System
1. Send Emergency Alert
2. Register User          ← NEW!
3. View System Status
4. Help
0. Exit
```

### Emergency Integration

When registered users send emergency alerts:
- ✅ Their location is automatically included
- ✅ Other users in the same location are notified
- ✅ More detailed location information is provided

## Data Models

### User Model
```python
class User(BaseModel):
    phone_number: str
    name: str
    location: str
    registration_date: str
```

### Session State Management
```python
class USSDSessionState:
    def get_session(self, session_id: str) -> Dict
    def set_session(self, session_id: str, data: Dict)
    def clear_session(self, session_id: str)
    def update_session(self, session_id: str, key: str, value)
```

## Testing the Features

### 1. Run the Test Suite
```bash
python test_user_features.py
```

This comprehensive test script covers:
- CSV upload functionality
- User management endpoints
- Location-based alerts
- USSD registration simulation
- Duplicate handling
- Emergency alerts with user context

### 2. Interactive USSD Testing
```bash
python enhanced_ussd_simulator.py
```

Features:
- Interactive USSD navigation
- Registration flow testing
- Session state visualization
- Command history
- Registration status checking

### 3. Manual CSV Upload Test
```bash
# Upload the sample CSV file
curl -X POST "http://localhost:8000/upload-users" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_users.csv"
```

### 4. Manual API Testing

**Get all users:**
```bash
curl "http://localhost:8000/users"
```

**Get users in Westlands:**
```bash
curl "http://localhost:8000/users/location/Westlands"
```

**Send location alert:**
```bash
curl -X POST "http://localhost:8000/send-location-alert" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "location=Westlands&message=Test alert message"
```

## File Structure

```
kasa/
├── main.py                           # Main FastAPI application
├── sample_users.csv                  # Sample CSV for testing
├── test_user_features.py             # Comprehensive test suite
├── enhanced_ussd_simulator.py        # Interactive USSD simulator
├── requirements.txt                  # Python dependencies
├── .env                             # Environment configuration
└── [existing files...]
```

## Usage Examples

### USSD Registration Example

```
User dials *123#
→ CON Welcome to KASA - Local Alert System
  1. Send Emergency Alert
  2. Register User
  3. View System Status
  4. Help
  0. Exit

User enters: 2
→ CON Enter your full name:

User enters: John Doe
→ CON Hello John Doe!
  Enter your location/area:

User enters: Westlands
→ CON Confirm registration:
  Name: John Doe
  Location: Westlands
  1. Confirm
  2. Cancel
  0. Main Menu

User enters: 1
→ END Registration successful!
  Name: John Doe
  Location: Westlands
  Phone: +254711123456
  You can now receive location alerts!
```

### Emergency Alert with Location Integration

```
Registered user dials *123# and selects emergency
→ Emergency alert sent to all users in the same location
→ Location-specific information included in SMS
→ More detailed response with user context
```

## Production Considerations

### Database Integration
Currently uses in-memory storage. For production:

```python
# Replace in-memory storage with database
users_db: Dict[str, User] = {}  # Current
# With database:
# from sqlalchemy import create_engine
# from models import User, SessionLocal
```

### Security
- Add authentication for admin endpoints
- Validate CSV file size limits
- Rate limiting for USSD requests
- Input sanitization

### Scalability
- Database connection pooling
- Caching for location queries
- Background task queues for bulk operations
- Session storage in Redis

### Monitoring
- User registration metrics
- Location alert delivery tracking
- USSD session analytics
- Error rate monitoring

## Next Steps

1. **Authentication Integration**: Add auth for admin endpoints
2. **Database Migration**: Move from in-memory to persistent storage
3. **Advanced Location Features**: GPS coordinates, geofencing
4. **Notification Preferences**: User-customizable alert types
5. **Analytics Dashboard**: User engagement and system metrics
6. **Multi-language Support**: USSD menus in local languages

## Troubleshooting

### Common Issues

**CSV Upload Fails:**
- Check CSV format (name,phone,location headers)
- Ensure phone numbers include country code (+254...)
- Verify file is valid CSV format

**USSD Registration Not Working:**
- Check session state management
- Verify phone number format
- Check server logs for errors

**Location Alerts Not Sent:**
- Verify users exist in the specified location
- Check Africa's Talking credentials
- Review SMS sending logs

### Debug Commands

```bash
# Check registered users
curl "http://localhost:8000/users"

# Check system status
curl "http://localhost:8000/health"

# View emergency reports
curl "http://localhost:8000/emergency-reports"
```

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Run the test suite to verify functionality
3. Use the enhanced USSD simulator for interactive testing
4. Review the FastAPI docs at http://localhost:8000/docs
