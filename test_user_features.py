#!/usr/bin/env python3
"""
KASA User Management Features Testing Script

This script demonstrates and tests:
1. User registration via CSV upload
2. USSD user registration simulation
3. Location-based user queries
4. Location-based alert sending
5. User management endpoints

Run this script to test all the new user management features.
"""

import requests
import json
import csv
import io
import time

# Configuration
BASE_URL = "http://localhost:8000"

def print_separator(title):
    """Print a visual separator for test sections"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_json_response(response, title="Response"):
    """Pretty print JSON response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        if response.headers.get('content-type', '').startswith('application/json'):
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text)
    except:
        print(response.text)

def test_csv_upload():
    """Test CSV upload functionality"""
    print_separator("Testing CSV User Upload")
    
    # Create sample CSV data
    csv_data = """name,phone,location
John Doe,+254711123456,Nairobi CBD
Jane Smith,+254712234567,Westlands
Bob Johnson,+254720345678,Kilimani
Alice Brown,+254733456789,Eastlands
Charlie Wilson,+254744567890,Karen
Diana Ross,+254755678901,Ngong Road"""
    
    print("Sample CSV data:")
    print(csv_data)
    
    # Create a file-like object
    files = {
        'file': ('users.csv', io.StringIO(csv_data), 'text/csv')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/upload-users", files=files)
        print_json_response(response, "CSV Upload Result")
    except requests.exceptions.RequestException as e:
        print(f"Error uploading CSV: {e}")

def test_user_endpoints():
    """Test user management endpoints"""
    print_separator("Testing User Management Endpoints")
    
    # Get all users
    print("\n1. Getting all users:")
    try:
        response = requests.get(f"{BASE_URL}/users")
        print_json_response(response, "All Users")
    except requests.exceptions.RequestException as e:
        print(f"Error getting users: {e}")
    
    # Get users by location
    print("\n2. Getting users in Westlands:")
    try:
        response = requests.get(f"{BASE_URL}/users/location/Westlands")
        print_json_response(response, "Users in Westlands")
    except requests.exceptions.RequestException as e:
        print(f"Error getting users by location: {e}")
    
    # Get users by location (case insensitive test)
    print("\n3. Getting users in NAIROBI CBD (testing case insensitivity):")
    try:
        response = requests.get(f"{BASE_URL}/users/location/NAIROBI CBD")
        print_json_response(response, "Users in NAIROBI CBD")
    except requests.exceptions.RequestException as e:
        print(f"Error getting users by location: {e}")

def test_location_alerts():
    """Test location-based alert functionality"""
    print_separator("Testing Location-based Alerts")
    
    # Send alert to Westlands
    print("\n1. Sending alert to Westlands users:")
    alert_data = {
        'location': 'Westlands',
        'message': 'Traffic jam on Waiyaki Way. Use alternative routes.'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/send-location-alert", data=alert_data)
        print_json_response(response, "Location Alert to Westlands")
    except requests.exceptions.RequestException as e:
        print(f"Error sending location alert: {e}")
    
    # Send alert to non-existent location
    print("\n2. Sending alert to non-existent location:")
    alert_data = {
        'location': 'Mars',
        'message': 'Alien invasion alert!'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/send-location-alert", data=alert_data)
        print_json_response(response, "Location Alert to Mars")
    except requests.exceptions.RequestException as e:
        print(f"Error sending location alert: {e}")

def simulate_ussd_registration():
    """Simulate USSD registration flow"""
    print_separator("Simulating USSD User Registration")
    
    # Simulate a new user registering via USSD
    print("\nSimulating USSD registration for +254766123456")
    
    session_id = "ATUid_test_registration_123"
    phone_number = "+254766123456"
    
    # Step 1: User dials USSD code and selects option 2 (Register)
    print("\n1. User dials USSD and selects 'Register User' (option 2):")
    try:
        response = requests.post(f"{BASE_URL}/ussd", data={
            'sessionId': session_id,
            'serviceCode': '*123#',
            'phoneNumber': phone_number,
            'text': '2'
        })
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error in USSD step 1: {e}")
    
    time.sleep(1)
    
    # Step 2: User enters their name
    print("\n2. User enters name 'Michael Test':")
    try:
        response = requests.post(f"{BASE_URL}/ussd", data={
            'sessionId': session_id,
            'serviceCode': '*123#',
            'phoneNumber': phone_number,
            'text': 'Michael Test'
        })
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error in USSD step 2: {e}")
    
    time.sleep(1)
    
    # Step 3: User enters their location
    print("\n3. User enters location 'Parklands':")
    try:
        response = requests.post(f"{BASE_URL}/ussd", data={
            'sessionId': session_id,
            'serviceCode': '*123#',
            'phoneNumber': phone_number,
            'text': 'Parklands'
        })
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error in USSD step 3: {e}")
    
    time.sleep(1)
    
    # Step 4: User confirms registration
    print("\n4. User confirms registration (option 1):")
    try:
        response = requests.post(f"{BASE_URL}/ussd", data={
            'sessionId': session_id,
            'serviceCode': '*123#',
            'phoneNumber': phone_number,
            'text': '1'
        })
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error in USSD step 4: {e}")

def test_duplicate_registration():
    """Test duplicate registration handling"""
    print_separator("Testing Duplicate Registration Handling")
    
    # Try to register the same user again via USSD
    print("\nTesting duplicate registration for +254711123456 (should already be registered from CSV):")
    
    session_id = "ATUid_test_duplicate_123"
    phone_number = "+254711123456"  # This user was in the CSV
    
    try:
        response = requests.post(f"{BASE_URL}/ussd", data={
            'sessionId': session_id,
            'serviceCode': '*123#',
            'phoneNumber': phone_number,
            'text': '2'  # Select register option
        })
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error testing duplicate registration: {e}")

def test_emergency_with_user():
    """Test emergency alert with registered user"""
    print_separator("Testing Emergency Alert with Registered User")
    
    # Simulate emergency alert from a registered user
    print("\nSimulating fire emergency from registered user +254711123456:")
    
    session_id = "ATUid_emergency_test_123"
    phone_number = "+254711123456"  # This user should be registered
    
    # User selects emergency (1), then fire (1), then confirms (1)
    try:
        response = requests.post(f"{BASE_URL}/ussd", data={
            'sessionId': session_id,
            'serviceCode': '*123#',
            'phoneNumber': phone_number,
            'text': '1*1*1'  # Emergency > Fire > Confirm
        })
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error in emergency test: {e}")

def test_system_status():
    """Test system status and overview"""
    print_separator("Testing System Status")
    
    # Get root endpoint (system overview)
    print("\n1. Getting system overview:")
    try:
        response = requests.get(f"{BASE_URL}/")
        print_json_response(response, "System Overview")
    except requests.exceptions.RequestException as e:
        print(f"Error getting system overview: {e}")
    
    # Get emergency reports
    print("\n2. Getting emergency reports:")
    try:
        response = requests.get(f"{BASE_URL}/emergency-reports")
        print_json_response(response, "Emergency Reports")
    except requests.exceptions.RequestException as e:
        print(f"Error getting emergency reports: {e}")

def main():
    """Run all tests"""
    print("KASA User Management Features Test Suite")
    print(f"Testing against: {BASE_URL}")
    print("Make sure the KASA server is running (python main.py)")
    
    try:
        # Test server connectivity
        response = requests.get(f"{BASE_URL}/health")
        print(f"\nServer health check: {response.status_code}")
    except requests.exceptions.RequestException:
        print(f"\n❌ Could not connect to server at {BASE_URL}")
        print("Make sure the server is running with: python main.py")
        return
    
    # Run all tests
    test_csv_upload()
    test_user_endpoints()
    test_location_alerts()
    simulate_ussd_registration()
    test_duplicate_registration()
    test_emergency_with_user()
    test_system_status()
    
    print_separator("Test Suite Complete")
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Check the server logs to see the detailed processing")
    print("2. Try the interactive USSD simulator: python ussd_simulator.py")
    print("3. Upload your own CSV file via the /upload-users endpoint")
    print("4. Use the FastAPI docs at http://localhost:8000/docs")

if __name__ == "__main__":
    main()
