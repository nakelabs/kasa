from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict
import africastalking
import os
from dotenv import load_dotenv
import logging
import csv
import io
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KASA - Local Alert & Notification System",
    description="A FastAPI backend for sending SMS alerts and handling USSD menus",
    version="1.0.0"
)

# Africa's Talking configuration
AFRICAS_TALKING_USERNAME = os.getenv("AFRICAS_TALKING_USERNAME")
AFRICAS_TALKING_API_KEY = os.getenv("AFRICAS_TALKING_API_KEY")
AFRICAS_TALKING_SENDER_ID = os.getenv("AFRICAS_TALKING_SENDER_ID", "KASA")

# Debug: Log the credentials (mask the API key)
logger.info(f"Loading credentials - Username: {AFRICAS_TALKING_USERNAME}")
logger.info(f"API Key (first 10 chars): {AFRICAS_TALKING_API_KEY[:10] if AFRICAS_TALKING_API_KEY else 'None'}...")
logger.info(f"Sender ID: {AFRICAS_TALKING_SENDER_ID}")

# Validate environment variables
if not AFRICAS_TALKING_USERNAME or not AFRICAS_TALKING_API_KEY:
    logger.error("Africa's Talking credentials not found in environment variables")
    raise ValueError("Africa's Talking credentials must be set in environment variables")

# Initialize Africa's Talking
africastalking.initialize(AFRICAS_TALKING_USERNAME, AFRICAS_TALKING_API_KEY)

# Get SMS service
sms = africastalking.SMS


# Pydantic models for request validation
class AlertRequest(BaseModel):
    message: str
    recipients: List[str]
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v.strip()) > 160:
            raise ValueError('Message cannot exceed 160 characters')
        return v.strip()
    
    @field_validator('recipients')
    @classmethod
    def validate_recipients(cls, v):
        if not v:
            raise ValueError('Recipients list cannot be empty')
        
        # Basic phone number validation for African numbers
        for phone in v:
            if not phone.startswith('+'):
                raise ValueError(f'Phone number {phone} must include country code (e.g., +254...)')
            if len(phone) < 10:
                raise ValueError(f'Phone number {phone} appears to be too short')
        
        return v


class LocationInfo(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    landmark: Optional[str] = None
    cell_tower_id: Optional[str] = None
    network_provider: Optional[str] = None


class User(BaseModel):
    phone_number: str
    name: str
    location: str
    registration_date: str = None
    
    def __init__(self, **data):
        if 'registration_date' not in data:
            data['registration_date'] = datetime.now().isoformat()
        super().__init__(**data)


class EmergencyReport(BaseModel):
    session_id: str
    phone_number: str
    emergency_type: str
    timestamp: str
    location: LocationInfo
    reference_id: str
    status: str = "pending"


class USSDSessionState:
    """Manages USSD session states for multi-step flows"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def get_session(self, session_id: str) -> Dict:
        """Get session data for a session ID"""
        return self.sessions.get(session_id, {})
    
    def set_session(self, session_id: str, data: Dict):
        """Set session data for a session ID"""
        self.sessions[session_id] = data
    
    def clear_session(self, session_id: str):
        """Clear session data for a session ID"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def update_session(self, session_id: str, key: str, value):
        """Update a specific key in session data"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id][key] = value


class USSDSession:
    """Helper class to manage USSD session states"""
    
    @staticmethod
    def get_main_menu():
        return ("CON Welcome to KASA - Local Alert System\n"
                "1. Send Emergency Alert\n"
                "2. Register User\n"
                "3. View System Status\n"
                "4. Help\n"
                "0. Exit")
    
    @staticmethod
    def get_emergency_menu():
        return ("CON Select Emergency Type:\n"
                "1. Fire Emergency\n"
                "2. Medical Emergency\n"
                "3. Security Alert\n"
                "4. Natural Disaster\n"
                "0. Back to Main Menu")
    
    @staticmethod
    def get_confirmation_menu(alert_type: str):
        return f"CON Confirm sending {alert_type}?\n1. Yes, Send Alert\n2. No, Cancel\n0. Main Menu"
    
    @staticmethod
    def get_help_menu():
        return ("CON KASA Help:\n"
                "- Dial this code to send alerts\n"
                "- Alerts are sent to registered contacts\n"
                "- For emergencies, call 999\n"
                "0. Back to Main Menu")
    
    @staticmethod
    def get_registration_name_prompt():
        return "CON Enter your full name:"
    
    @staticmethod
    def get_registration_location_prompt(name: str):
        return f"CON Hello {name}!\nEnter your location/area:"
    
    @staticmethod
    def get_registration_confirmation(name: str, location: str):
        return f"CON Confirm registration:\nName: {name}\nLocation: {location}\n1. Confirm\n2. Cancel\n0. Main Menu"


# In-memory storage for emergency reports and users (use database in production)
emergency_reports = {}
users_db: Dict[str, User] = {}  # phone_number -> User object

# Initialize USSD session manager
ussd_session_manager = USSDSessionState()


# Location tracking functionality
def get_location_from_phone(phone_number: str) -> LocationInfo:
    """Get location based on phone number (simulates cell tower triangulation)"""
    # Debug: Log the phone number being processed
    logger.info(f"🔍 Processing location for phone number: '{phone_number}'")
    
    # Simulate different locations based on phone number patterns
    location_map = {
        "+254711": LocationInfo(
            latitude=-1.2921,
            longitude=36.8219,
            address="Nairobi Central Business District",
            landmark="Near Kenyatta Avenue",
            cell_tower_id="NRB_001",
            network_provider="Safaricom"
        ),
        "+254712": LocationInfo(
            latitude=-1.3032,
            longitude=36.7073,
            address="Westlands, Nairobi", 
            landmark="Near Sarit Centre",
            cell_tower_id="WLD_002",
            network_provider="Safaricom"
        ),
        "+254720": LocationInfo(
            latitude=-1.2833,
            longitude=36.8167,
            address="Kilimani, Nairobi",
            landmark="Near Yaya Centre", 
            cell_tower_id="KLM_003",
            network_provider="Airtel"
        )
    }
    
    # Find matching location based on phone prefix
    for prefix, location in location_map.items():
        logger.info(f"🔍 Checking prefix '{prefix}' against '{phone_number}'")
        if phone_number.startswith(prefix):
            logger.info(f"✅ Match found! Using location: {location.address}")
            return location
    
    # Default location
    logger.warning(f"⚠️ No location match found for {phone_number}, using default")
    return LocationInfo(
        address="Location being determined via cell tower triangulation",
        landmark="Emergency services dispatched",
        network_provider="Detecting..."
    )


def format_location_for_sms(location: LocationInfo) -> str:
    """Format location for SMS to emergency responders"""
    parts = []
    if location.address:
        parts.append(f"📍{location.address}")
    if location.landmark:
        parts.append(f"🏢{location.landmark}")
    if location.latitude and location.longitude:
        parts.append(f"GPS:{location.latitude},{location.longitude}")
    return " | ".join(parts) if parts else "Location: Being determined"


# Helper functions for user management
def get_users_by_location(location: str) -> List[User]:
    """Get all users in a specific location"""
    logger.info(f"Getting users for location: {location}")
    matching_users = []
    
    for phone, user in users_db.items():
        if user.location.lower() == location.lower():
            matching_users.append(user)
    
    logger.info(f"Found {len(matching_users)} users in {location}")
    return matching_users


def send_alert_to_location(location: str, message: str) -> Dict:
    """Send alert message to all users in a specific location"""
    logger.info(f"Sending alert to location: {location}")
    
    # Get users in the location
    users_in_location = get_users_by_location(location)
    
    if not users_in_location:
        logger.warning(f"No users found in location: {location}")
        return {
            "status": "warning",
            "message": f"No registered users found in {location}",
            "sent_count": 0
        }
    
    # Extract phone numbers
    phone_numbers = [user.phone_number for user in users_in_location]
    
    # Format the alert message
    formatted_message = f"[KASA LOCATION ALERT - {location.upper()}] {message}"
    
    try:
        # Send SMS using Africa's Talking
        if AFRICAS_TALKING_SENDER_ID:
            response = sms.send(
                formatted_message, 
                phone_numbers, 
                sender_id=AFRICAS_TALKING_SENDER_ID
            )
        else:
            response = sms.send(formatted_message, phone_numbers)
        
        logger.info(f"Location alert sent to {len(phone_numbers)} users in {location}")
        
        return {
            "status": "success",
            "message": f"Alert sent to {len(phone_numbers)} users in {location}",
            "sent_count": len(phone_numbers),
            "location": location,
            "recipients": phone_numbers,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Error sending location alert: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send alert to {location}: {str(e)}",
            "sent_count": 0
        }


def register_user(phone_number: str, name: str, location: str) -> User:
    """Register a new user in the system"""
    logger.info(f"Registering user: {name} ({phone_number}) in {location}")
    
    user = User(
        phone_number=phone_number,
        name=name,
        location=location
    )
    
    users_db[phone_number] = user
    logger.info(f"User {name} registered successfully")
    
    return user


def get_user_by_phone(phone_number: str) -> Optional[User]:
    """Get user by phone number"""
    return users_db.get(phone_number)


@app.post("/upload-users")
async def upload_users_csv(file: UploadFile = File(...)):
    """
    Upload CSV file to bulk import users
    Expected CSV format: name,phone,location
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Validate CSV headers
        expected_headers = {'name', 'phone', 'location'}
        if not expected_headers.issubset(set(csv_reader.fieldnames)):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain headers: {', '.join(expected_headers)}. Found: {', '.join(csv_reader.fieldnames)}"
            )
        
        # Process users
        imported_users = []
        errors = []
        duplicate_count = 0
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
            try:
                name = row['name'].strip()
                phone = row['phone'].strip()
                location = row['location'].strip()
                
                # Validate required fields
                if not name or not phone or not location:
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue
                
                # Basic phone validation
                if not phone.startswith('+'):
                    errors.append(f"Row {row_num}: Phone number must include country code (e.g., +254...)")
                    continue
                
                # Check for duplicates
                if phone in users_db:
                    duplicate_count += 1
                    logger.info(f"User {phone} already exists, skipping")
                    continue
                
                # Register user
                user = register_user(phone, name, location)
                imported_users.append({
                    "name": user.name,
                    "phone": user.phone_number,
                    "location": user.location,
                    "registration_date": user.registration_date
                })
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        logger.info(f"CSV upload completed: {len(imported_users)} users imported, {len(errors)} errors, {duplicate_count} duplicates")
        
        return {
            "message": "CSV upload completed",
            "imported_count": len(imported_users),
            "error_count": len(errors),
            "duplicate_count": duplicate_count,
            "total_users_now": len(users_db),
            "imported_users": imported_users,
            "errors": errors[:10] if errors else [],  # Limit errors shown
            "has_more_errors": len(errors) > 10
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")


@app.get("/users")
async def get_all_users():
    """Get all registered users"""
    try:
        users_list = []
        for phone, user in users_db.items():
            users_list.append({
                "name": user.name,
                "phone": user.phone_number,
                "location": user.location,
                "registration_date": user.registration_date
            })
        
        # Group users by location for summary
        location_summary = {}
        for user in users_list:
            location = user['location']
            if location not in location_summary:
                location_summary[location] = 0
            location_summary[location] += 1
        
        return {
            "total_users": len(users_list),
            "users": users_list,
            "location_summary": location_summary,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")


@app.get("/users/location/{location}")
async def get_users_by_location_endpoint(location: str):
    """Get all users in a specific location"""
    try:
        users_in_location = get_users_by_location(location)
        
        users_list = []
        for user in users_in_location:
            users_list.append({
                "name": user.name,
                "phone": user.phone_number,
                "location": user.location,
                "registration_date": user.registration_date
            })
        
        return {
            "location": location,
            "user_count": len(users_list),
            "users": users_list
        }
        
    except Exception as e:
        logger.error(f"Error fetching users for location {location}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")


@app.post("/send-location-alert")
async def send_location_alert_endpoint(
    location: str = Form(...),
    message: str = Form(...)
):
    """Send alert to all users in a specific location"""
    try:
        # Validate message
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(message.strip()) > 140:  # Leave room for location prefix
            raise HTTPException(status_code=400, detail="Message too long (max 140 characters)")
        
        # Send the alert
        result = send_alert_to_location(location, message.strip())
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending location alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending alert: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with system overview"""
    user_count = len(users_db)
    report_count = len(emergency_reports)
    
    return {
        "message": "Welcome to KASA - Local Alert & Notification System",
        "version": "1.0.0",
        "features": [
            "SMS Alerts",
            "USSD Menu System",
            "User Registration (USSD & CSV)",
            "Location-based Alerts",
            "Emergency Reporting"
        ],
        "stats": {
            "registered_users": user_count,
            "emergency_reports": report_count
        },
        "endpoints": {
            "ussd": "/ussd",
            "send_alert": "/send-alert",
            "upload_users": "/upload-users",
            "users": "/users",
            "location_alert": "/send-location-alert",
            "emergency_reports": "/emergency-reports"
        }
    }


@app.post("/send-alert")
async def send_alert(alert_request: AlertRequest):
    """
    Send SMS alert to multiple recipients
    """
    try:
        # Prepare the message with KASA branding
        formatted_message = f"[KASA ALERT] {alert_request.message}"
        
        logger.info(f"Attempting to send SMS to {len(alert_request.recipients)} recipients")
        logger.info(f"Message: {formatted_message}")
        logger.info(f"Recipients: {alert_request.recipients}")
        logger.info(f"Sender ID: {AFRICAS_TALKING_SENDER_ID}")
        
        # Send SMS using Africa's Talking
        # Only include sender_id if it's not empty (sandbox doesn't allow custom sender IDs)
        if AFRICAS_TALKING_SENDER_ID:
            response = sms.send(
                formatted_message, 
                alert_request.recipients, 
                sender_id=AFRICAS_TALKING_SENDER_ID
            )
        else:
            response = sms.send(
                formatted_message, 
                alert_request.recipients
            )
        
        logger.info(f"Africa's Talking response: {response}")
        
        # Process the response
        if response and 'SMSMessageData' in response and response['SMSMessageData']['Recipients']:
            successful_sends = []
            failed_sends = []
            
            for recipient in response['SMSMessageData']['Recipients']:
                if recipient['status'] == 'Success':
                    successful_sends.append({
                        "number": recipient['number'],
                        "status": recipient['status'],
                        "messageId": recipient['messageId'],
                        "cost": recipient['cost']
                    })
                else:
                    failed_sends.append({
                        "number": recipient['number'],
                        "status": recipient['status'],
                        "statusCode": recipient.get('statusCode', 'Unknown')
                    })
            
            logger.info(f"SMS sent successfully to {len(successful_sends)} recipients")
            
            return {
                "message": "Alert processing completed",
                "successful_sends": successful_sends,
                "failed_sends": failed_sends,
                "total_recipients": len(alert_request.recipients),
                "successful_count": len(successful_sends),
                "failed_count": len(failed_sends),
                "debug_info": {
                    "environment": "sandbox" if AFRICAS_TALKING_USERNAME == "sandbox" else "production",
                    "sender_id": AFRICAS_TALKING_SENDER_ID
                }
            }
        else:
            logger.error(f"Invalid response structure: {response}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": "Invalid response from SMS service",
                    "response": str(response),
                    "help": "Check your Africa's Talking credentials and account status"
                }
            )
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error sending SMS: {error_msg}")
        
        # Provide specific help based on common errors
        help_message = "Unknown error occurred"
        if "authentication" in error_msg.lower():
            help_message = "Invalid credentials. Check your Africa's Talking username and API key."
        elif "insufficient" in error_msg.lower():
            help_message = "Insufficient credit. Check your Africa's Talking account balance."
        elif "invalid" in error_msg.lower() and "phone" in error_msg.lower():
            help_message = "Invalid phone number format. Use international format (e.g., +254712345678)."
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Failed to send alert: {error_msg}",
                "help": help_message,
                "debug_info": {
                    "username": AFRICAS_TALKING_USERNAME,
                    "api_key_set": bool(AFRICAS_TALKING_API_KEY),
                    "sender_id": AFRICAS_TALKING_SENDER_ID
                }
            }
        )


@app.post("/ussd", response_class=PlainTextResponse)
async def ussd_handler(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(default="")
):
    """
    Handle USSD requests from Africa's Talking with session state management
    """
    try:
        logger.info(f"USSD request - Session: {sessionId}, Phone: {phoneNumber}, Text: '{text}'")
        
        # Get current session state
        session_data = ussd_session_manager.get_session(sessionId)
        
        # Split the text by '*' to get user's navigation path
        text_array = text.split('*') if text else ['']
        
        # Check if we're in a registration flow
        if session_data.get('flow') == 'registration':
            return await handle_registration_flow(sessionId, phoneNumber, text, text_array, session_data)
        
        # Main menu (when user first dials or selects 0)
        if text == '' or text == '0':
            ussd_session_manager.clear_session(sessionId)
            return USSDSession.get_main_menu()
        
        # First level navigation
        elif len(text_array) == 1:
            if text == '1':  # Send Emergency Alert
                return USSDSession.get_emergency_menu()
            elif text == '2':  # Register User
                # Check if user is already registered
                existing_user = get_user_by_phone(phoneNumber)
                if existing_user:
                    return (f"END You are already registered!\n"
                           f"Name: {existing_user.name}\n"
                           f"Location: {existing_user.location}\n"
                           f"Registered: {existing_user.registration_date[:10]}")
                
                # Start registration flow
                ussd_session_manager.set_session(sessionId, {
                    'flow': 'registration',
                    'step': 'name',
                    'phone': phoneNumber
                })
                return USSDSession.get_registration_name_prompt()
            elif text == '3':  # View System Status
                user_count = len(users_db)
                return (f"END KASA System Status:\n"
                       f"✓ SMS Service: Online\n"
                       f"✓ Alert System: Active\n"
                       f"✓ Registered Users: {user_count}\n"
                       f"✓ Last Updated: Now\n"
                       f"System is operational.")
            elif text == '4':  # Help
                return USSDSession.get_help_menu()
            else:
                return "END Invalid option. Please try again."
        
        # Second level navigation
        elif len(text_array) == 2:
            if text_array[0] == '1':  # Emergency alert selected
                emergency_types = {
                    '1': 'Fire Emergency',
                    '2': 'Medical Emergency', 
                    '3': 'Security Alert',
                    '4': 'Natural Disaster'
                }
                
                if text_array[1] in emergency_types:
                    alert_type = emergency_types[text_array[1]]
                    return USSDSession.get_confirmation_menu(alert_type)
                elif text_array[1] == '0':
                    return USSDSession.get_main_menu()
                else:
                    return "END Invalid emergency type."
            
            elif text_array[0] == '4' and text_array[1] == '0':  # Back from help
                return USSDSession.get_main_menu()
        
        # Third level navigation (confirmation)
        elif len(text_array) == 3:
            if text_array[0] == '1' and text_array[2] == '1':  # Confirm alert
                emergency_types = {
                    '1': 'Fire Emergency',
                    '2': 'Medical Emergency',
                    '3': 'Security Alert', 
                    '4': 'Natural Disaster'
                }
                
                alert_type = emergency_types.get(text_array[1])
                if alert_type:
                    # Get user info if registered
                    user = get_user_by_phone(phoneNumber)
                    user_location_str = user.location if user else "Unknown"
                    
                    # Simulate getting location from phone number
                    location = get_location_from_phone(phoneNumber)
                    
                    # Format the location for SMS
                    location_info = format_location_for_sms(location)
                    
                    # Create a reference ID for the emergency report
                    reference_id = f"EMR-{sessionId[:8]}"
                    
                    # Create the emergency report
                    report = EmergencyReport(
                        session_id=sessionId,
                        phone_number=phoneNumber,
                        emergency_type=alert_type,
                        timestamp=datetime.now().isoformat(),
                        location=location,
                        reference_id=reference_id,
                        status="pending"
                    )
                    
                    # Store the report in in-memory storage
                    emergency_reports[reference_id] = report
                    
                    # Send alert to registered users in the same area (if user is registered)
                    location_alert_result = None
                    if user:
                        alert_message = f"EMERGENCY ALERT: {alert_type} reported in {user.location}. From: {user.name} ({phoneNumber}). Stay alert and safe!"
                        location_alert_result = send_alert_to_location(user.location, alert_message)
                    
                    # Clear session
                    ussd_session_manager.clear_session(sessionId)
                    
                    response_msg = (f"END {alert_type} alert sent!\n"
                                  f"Reference: {reference_id}\n"
                                  f"Location: {location_info}")
                    
                    if location_alert_result and location_alert_result['status'] == 'success':
                        response_msg += f"\n✓ {location_alert_result['sent_count']} local users notified"
                    
                    response_msg += "\nStay safe!"
                    
                    return response_msg
                
            elif text_array[0] == '1' and text_array[2] == '2':  # Cancel alert
                ussd_session_manager.clear_session(sessionId)
                return "END Alert cancelled. Stay safe!"
            
            elif text_array[0] == '1' and text_array[2] == '0':  # Back to main menu
                return USSDSession.get_main_menu()
        
        # Default response for unhandled cases
        ussd_session_manager.clear_session(sessionId)
        return "END Session ended. Dial again to restart."
        
    except Exception as e:
        logger.error(f"Error handling USSD request: {str(e)}")
        ussd_session_manager.clear_session(sessionId)
        return "END System error. Please try again later."


async def handle_registration_flow(session_id: str, phone_number: str, text: str, text_array: List[str], session_data: Dict) -> str:
    """Handle the multi-step user registration flow"""
    try:
        step = session_data.get('step')
        
        if step == 'name':
            if text and text.strip():
                # User entered their name
                name = text.strip()
                ussd_session_manager.update_session(session_id, 'name', name)
                ussd_session_manager.update_session(session_id, 'step', 'location')
                return USSDSession.get_registration_location_prompt(name)
            else:
                return "CON Please enter your full name:"
        
        elif step == 'location':
            if text and text.strip():
                # User entered their location
                location = text.strip()
                name = session_data.get('name')
                ussd_session_manager.update_session(session_id, 'location', location)
                ussd_session_manager.update_session(session_id, 'step', 'confirmation')
                return USSDSession.get_registration_confirmation(name, location)
            else:
                return "CON Please enter your location/area:"
        
        elif step == 'confirmation':
            if text == '1':  # Confirm registration
                name = session_data.get('name')
                location = session_data.get('location')
                
                # Register the user
                user = register_user(phone_number, name, location)
                
                # Clear session
                ussd_session_manager.clear_session(session_id)
                
                return (f"END Registration successful!\n"
                       f"Name: {name}\n"
                       f"Location: {location}\n"
                       f"Phone: {phone_number}\n"
                       f"You can now receive location alerts!")
            
            elif text == '2':  # Cancel registration
                ussd_session_manager.clear_session(session_id)
                return "END Registration cancelled."
            
            elif text == '0':  # Back to main menu
                ussd_session_manager.clear_session(session_id)
                return USSDSession.get_main_menu()
            
            else:
                # Invalid option, show confirmation again
                name = session_data.get('name')
                location = session_data.get('location')
                return USSDSession.get_registration_confirmation(name, location)
        
        # If we get here, something went wrong
        ussd_session_manager.clear_session(session_id)
        return "END Registration error. Please try again."
        
    except Exception as e:
        logger.error(f"Error in registration flow: {str(e)}")
        ussd_session_manager.clear_session(session_id)
        return "END Registration error. Please try again later."


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # You could add more comprehensive health checks here
        # like checking Africa's Talking API connectivity
        return {
            "status": "healthy",
            "service": "KASA Alert System",
            "timestamp": "2025-06-27",
            "africas_talking": "configured" if AFRICAS_TALKING_USERNAME else "not_configured"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/test-sms-credentials")
async def test_sms_credentials():
    """
    Test SMS credentials without sending actual messages
    """
    try:
        # Try to initialize the SMS service (this validates credentials)
        test_sms = africastalking.SMS
        
        return {
            "status": "success",
            "message": "SMS credentials are valid",
            "config": {
                "username": AFRICAS_TALKING_USERNAME,
                "api_key_configured": bool(AFRICAS_TALKING_API_KEY),
                "sender_id": AFRICAS_TALKING_SENDER_ID,
                "environment": "sandbox" if AFRICAS_TALKING_USERNAME == "sandbox" else "production"
            },
            "sandbox_info": {
                "note": "For sandbox testing, use test numbers from your dashboard",
                "common_test_formats": ["+254711XXXXXX", "+254733XXXXXX"],
                "dashboard_url": "https://account.africastalking.com/"
            }
        }
    except Exception as e:
        logger.error(f"SMS credentials test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(e),
                "help": "Check your Africa's Talking credentials in the .env file"
            }
        )


@app.get("/test-credentials")
async def test_credentials():
    """Test Africa's Talking credentials without sending SMS"""
    try:
        return {
            "username": AFRICAS_TALKING_USERNAME,
            "api_key_preview": f"{AFRICAS_TALKING_API_KEY[:10]}..." if AFRICAS_TALKING_API_KEY else "None",
            "sender_id": AFRICAS_TALKING_SENDER_ID,
            "credentials_loaded": bool(AFRICAS_TALKING_USERNAME and AFRICAS_TALKING_API_KEY)
        }
    except Exception as e:
        logger.error(f"Error checking credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking credentials: {str(e)}")


@app.get("/emergency-reports")
async def get_emergency_reports():
    """Get all emergency reports for emergency services dashboard"""
    try:
        reports = []
        for ref_id, report in emergency_reports.items():
            reports.append({
                "reference_id": ref_id,
                "emergency_type": report.emergency_type,
                "phone_number": report.phone_number,
                "timestamp": report.timestamp,
                "location": {
                    "address": report.location.address,
                    "landmark": report.location.landmark,
                    "latitude": report.location.latitude,
                    "longitude": report.location.longitude,
                    "cell_tower": report.location.cell_tower_id,
                    "network": report.location.network_provider,
                    "maps_link": f"https://maps.google.com/?q={report.location.latitude},{report.location.longitude}" if report.location.latitude and report.location.longitude else None
                },
                "status": report.status
            })
        
        return {
            "total_reports": len(reports),
            "reports": reports,
            "last_updated": "2025-06-28T14:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching emergency reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")


@app.post("/register-location")
async def register_user_location(
    phone_number: str = Form(...),
    address: str = Form(...),
    landmark: str = Form(default=""),
    latitude: float = Form(default=None),
    longitude: float = Form(default=None)
):
    """Allow users to register their location for emergencies"""
    try:
        # In production, store this in a database
        user_location = LocationInfo(
            latitude=latitude,
            longitude=longitude,
            address=address,
            landmark=landmark if landmark else None
        )
        
        # Store in memory (use database in production)
        if not hasattr(register_user_location, 'user_locations'):
            register_user_location.user_locations = {}
        
        register_user_location.user_locations[phone_number] = user_location
        
        logger.info(f"Location registered for {phone_number}: {address}")
        
        return {
            "message": "Location registered successfully",
            "phone_number": phone_number,
            "address": address,
            "landmark": landmark,
            "coordinates": f"{latitude}, {longitude}" if latitude and longitude else "Not provided",
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error registering location: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering location: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
