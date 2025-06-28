#!/usr/bin/env python3
"""
KASA Quick Start Script

This script helps you get started with the enhanced KASA system.
It will guide you through testing all the new user management features.
"""

import os
import sys
import subprocess
import time
import requests

def print_banner():
    print("\n" + "="*60)
    print("    KASA - Local Alert & Notification System")
    print("    User Management Features Quick Start")
    print("="*60)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'africastalking',
        'python-dotenv',
        'pydantic',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies are installed!")
    return True

def check_environment():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("  ❌ .env file not found")
        print("  Create .env file with your Africa's Talking credentials:")
        print("  AFRICAS_TALKING_USERNAME=your_username")
        print("  AFRICAS_TALKING_API_KEY=your_api_key")
        print("  AFRICAS_TALKING_SENDER_ID=KASA")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv("AFRICAS_TALKING_USERNAME")
    api_key = os.getenv("AFRICAS_TALKING_API_KEY")
    
    if not username or not api_key:
        print("  ❌ Missing credentials in .env file")
        return False
    
    print(f"  ✅ Username: {username}")
    print(f"  ✅ API Key: {'*' * 8}...{api_key[-4:] if api_key else 'None'}")
    return True

def start_server():
    """Start the FastAPI server in background"""
    print("\n🚀 Starting KASA server...")
    
    try:
        # Check if server is already running
        response = requests.get("http://localhost:8000/health", timeout=2)
        print("  ✅ Server is already running!")
        return True
    except:
        pass
    
    try:
        # Start server in background
        import subprocess
        import sys
        
        # Use subprocess to start the server
        if sys.platform.startswith('win'):
            server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8000"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8000"
            ])
        
        # Wait a moment for server to start
        print("  ⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Check if server is running
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Server started successfully!")
            return True
        else:
            print("  ❌ Server started but not responding correctly")
            return False
            
    except Exception as e:
        print(f"  ❌ Failed to start server: {e}")
        print("  Try manually running: python -m uvicorn main:app --host 0.0.0.0 --port 8000")
        return False

def show_menu():
    """Show the main menu options"""
    print("\n" + "="*60)
    print("    What would you like to test?")
    print("="*60)
    print("1. 📊 Run comprehensive test suite")
    print("2. 📱 Interactive USSD simulator")
    print("3. 📄 Upload sample CSV users")
    print("4. 🔍 Check system status")
    print("5. 📚 View API documentation")
    print("6. 📖 Read user guide")
    print("7. 🚪 Exit")
    
    return input("\nSelect option (1-7): ").strip()

def run_test_suite():
    """Run the comprehensive test suite"""
    print("\n🧪 Running comprehensive test suite...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_user_features.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except Exception as e:
        print(f"❌ Error running test suite: {e}")

def run_ussd_simulator():
    """Run the interactive USSD simulator"""
    print("\n📱 Starting interactive USSD simulator...")
    try:
        import subprocess
        subprocess.run([sys.executable, "enhanced_ussd_simulator.py"])
    except Exception as e:
        print(f"❌ Error running USSD simulator: {e}")

def upload_sample_csv():
    """Upload the sample CSV file"""
    print("\n📄 Uploading sample CSV users...")
    
    if not os.path.exists("sample_users.csv"):
        print("❌ sample_users.csv not found")
        return
    
    try:
        with open("sample_users.csv", 'rb') as f:
            files = {'file': ('sample_users.csv', f, 'text/csv')}
            response = requests.post("http://localhost:8000/upload-users", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Imported: {result.get('imported_count', 0)} users")
            print(f"   Errors: {result.get('error_count', 0)}")
            print(f"   Duplicates: {result.get('duplicate_count', 0)}")
        else:
            print(f"❌ Upload failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error uploading CSV: {e}")

def check_system_status():
    """Check and display system status"""
    print("\n🔍 Checking system status...")
    
    try:
        # Check main system
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print("✅ System Status:")
            print(f"   Version: {data.get('version', 'Unknown')}")
            stats = data.get('stats', {})
            print(f"   Registered Users: {stats.get('registered_users', 0)}")
            print(f"   Emergency Reports: {stats.get('emergency_reports', 0)}")
        
        # Check health
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        
        # Get user summary
        response = requests.get("http://localhost:8000/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User Database: {data.get('total_users', 0)} users")
            
            locations = data.get('location_summary', {})
            if locations:
                print("   Locations:")
                for location, count in locations.items():
                    print(f"     • {location}: {count} users")
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def open_api_docs():
    """Open API documentation in browser"""
    print("\n📚 Opening API documentation...")
    import webbrowser
    webbrowser.open("http://localhost:8000/docs")
    print("✅ API docs opened in your browser")

def show_user_guide():
    """Display the user guide"""
    print("\n📖 User Guide:")
    
    if os.path.exists("USER_MANAGEMENT_GUIDE.md"):
        print("Full guide available in: USER_MANAGEMENT_GUIDE.md")
    
    print("\n🚀 Quick Start:")
    print("1. Upload users via CSV: POST /upload-users")
    print("2. Register via USSD: Dial *123# → Option 2")
    print("3. Send location alerts: POST /send-location-alert")
    print("4. View users: GET /users")
    print("5. Emergency alerts: Dial *123# → Option 1")
    
    print("\n📱 USSD Menu:")
    print("*123# → 1. Emergency Alert")
    print("     → 2. Register User")
    print("     → 3. System Status")
    print("     → 4. Help")

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first: pip install -r requirements.txt")
        return
    
    # Check environment
    if not check_environment():
        print("\n❌ Please configure your .env file first")
        return
    
    # Start server
    if not start_server():
        print("\n❌ Please start the server manually and try again")
        return
    
    # Main menu loop
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_test_suite()
        elif choice == '2':
            run_ussd_simulator()
        elif choice == '3':
            upload_sample_csv()
        elif choice == '4':
            check_system_status()
        elif choice == '5':
            open_api_docs()
        elif choice == '6':
            show_user_guide()
        elif choice == '7':
            print("\n👋 Thanks for using KASA!")
            break
        else:
            print("❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
