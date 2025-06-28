#!/usr/bin/env python3
"""
Enhanced KASA USSD Simulator with User Registration

This interactive simulator allows you to test:
1. USSD navigation and menus
2. Multi-step user registration flow
3. Emergency alerts with location integration
4. Session state management

Run this to interactively test USSD flows.
"""

import requests
import uuid
import json

BASE_URL = "http://localhost:8000"

class USSDSimulator:
    def __init__(self):
        self.session_id = f"ATUid_sim_{uuid.uuid4().hex[:8]}"
        self.phone_number = None
        self.text_history = []
    
    def print_banner(self):
        print("\n" + "="*60)
        print("    KASA USSD Simulator - Enhanced with Registration")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print("Type 'quit' to exit, 'reset' to start over")
        print("Type 'help' for available commands")
    
    def get_phone_number(self):
        """Get phone number from user"""
        while not self.phone_number:
            phone = input("\nEnter your phone number (e.g., +254711123456): ").strip()
            if phone.startswith('+') and len(phone) >= 10:
                self.phone_number = phone
                print(f"✓ Using phone number: {phone}")
            else:
                print("❌ Please enter a valid phone number with country code (e.g., +254711123456)")
    
    def send_ussd_request(self, text):
        """Send USSD request to the server"""
        try:
            data = {
                'sessionId': self.session_id,
                'serviceCode': '*123#',
                'phoneNumber': self.phone_number,
                'text': text
            }
            
            response = requests.post(f"{BASE_URL}/ussd", data=data)
            return response.text
        except requests.exceptions.RequestException as e:
            return f"❌ Error: Could not connect to server. Make sure it's running at {BASE_URL}"
    
    def handle_command(self, user_input):
        """Handle special commands"""
        if user_input.lower() == 'quit':
            return False
        elif user_input.lower() == 'reset':
            self.session_id = f"ATUid_sim_{uuid.uuid4().hex[:8]}"
            self.text_history = []
            print(f"\n🔄 Session reset. New session ID: {self.session_id}")
            return True
        elif user_input.lower() == 'help':
            self.show_help()
            return True
        elif user_input.lower() == 'history':
            self.show_history()
            return True
        elif user_input.lower() == 'check':
            self.check_registration()
            return True
        return None
    
    def show_help(self):
        """Show help information"""
        print("\n📋 Available Commands:")
        print("  quit     - Exit the simulator")
        print("  reset    - Start a new USSD session")
        print("  help     - Show this help")
        print("  history  - Show your input history")
        print("  check    - Check if your number is registered")
        print("\n📱 USSD Navigation:")
        print("  1        - Send Emergency Alert")
        print("  2        - Register User (new!)")
        print("  3        - View System Status")
        print("  4        - Help")
        print("  0        - Exit/Back to main menu")
        print("\n🆕 Registration Flow:")
        print("  1. Select option 2 from main menu")
        print("  2. Enter your full name when prompted")
        print("  3. Enter your location/area")
        print("  4. Confirm registration (1=Yes, 2=No)")
    
    def show_history(self):
        """Show input history"""
        print("\n📝 Your Input History:")
        if not self.text_history:
            print("  (No inputs yet)")
        else:
            for i, text in enumerate(self.text_history, 1):
                print(f"  {i}. '{text}'")
    
    def check_registration(self):
        """Check if the current phone number is registered"""
        try:
            response = requests.get(f"{BASE_URL}/users")
            if response.status_code == 200:
                users_data = response.json()
                for user in users_data.get('users', []):
                    if user['phone'] == self.phone_number:
                        print(f"\n✅ You are registered!")
                        print(f"   Name: {user['name']}")
                        print(f"   Location: {user['location']}")
                        print(f"   Registered: {user['registration_date'][:10]}")
                        return
                print(f"\n❌ Phone number {self.phone_number} is not registered")
            else:
                print("❌ Could not check registration status")
        except requests.exceptions.RequestException:
            print("❌ Could not connect to server to check registration")
    
    def format_response(self, response_text):
        """Format and display the USSD response"""
        print(f"\n📱 USSD Response:")
        print("-" * 40)
        
        # Clean up the response
        if response_text.startswith('CON '):
            print("🔄 Continue...")
            print(response_text[4:])  # Remove 'CON ' prefix
            return True
        elif response_text.startswith('END '):
            print("✅ Session ended")
            print(response_text[4:])  # Remove 'END ' prefix
            return False
        else:
            print(response_text)
            return True
    
    def run(self):
        """Main simulator loop"""
        self.print_banner()
        self.get_phone_number()
        
        print(f"\n🚀 Starting USSD session for {self.phone_number}")
        print("Dialing *123#...")
        
        # Start with empty text (main menu)
        text = ""
        session_active = True
        
        while session_active:
            # Send USSD request
            response = self.send_ussd_request(text)
            
            # Display response
            continue_session = self.format_response(response)
            
            if not continue_session:
                print("\n🏁 USSD session ended")
                restart = input("\nStart a new session? (y/n): ").strip().lower()
                if restart == 'y':
                    self.session_id = f"ATUid_sim_{uuid.uuid4().hex[:8]}"
                    self.text_history = []
                    text = ""
                    session_active = True
                    continue
                else:
                    break
            
            # Get user input
            print("\n" + "-" * 40)
            user_input = input("Enter your choice: ").strip()
            
            # Handle special commands
            command_result = self.handle_command(user_input)
            if command_result is False:  # quit command
                break
            elif command_result is True:  # other commands handled
                continue
            
            # Add to history
            self.text_history.append(user_input)
            
            # Build text for next request
            if text == "":
                text = user_input
            else:
                text = text + "*" + user_input
        
        print("\n👋 Thanks for using KASA USSD Simulator!")

def test_registration_examples():
    """Show examples of how to test registration"""
    print("\n" + "="*60)
    print("    Registration Testing Examples")
    print("="*60)
    
    print("\n🎯 Example 1: New User Registration")
    print("1. Start simulator and enter a new phone number (e.g., +254799123456)")
    print("2. Select option '2' (Register User)")
    print("3. Enter name: 'Test User'")
    print("4. Enter location: 'Test Location'")
    print("5. Select '1' to confirm")
    
    print("\n🎯 Example 2: Duplicate Registration Test")
    print("1. Use a phone number that's already registered")
    print("2. Select option '2' (Register User)")
    print("3. Should show you're already registered")
    
    print("\n🎯 Example 3: Emergency with Location Alert")
    print("1. Use a registered phone number")
    print("2. Select option '1' (Emergency Alert)")
    print("3. Choose emergency type (e.g., '1' for Fire)")
    print("4. Confirm with '1'")
    print("5. Should notify other users in your location")

def main():
    print("KASA Enhanced USSD Simulator")
    print("\nOptions:")
    print("1. Interactive USSD Simulator")
    print("2. Show Registration Examples")
    print("3. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        simulator = USSDSimulator()
        simulator.run()
    elif choice == '2':
        test_registration_examples()
        input("\nPress Enter to continue...")
        main()
    elif choice == '3':
        print("Goodbye!")
    else:
        print("Invalid option. Please try again.")
        main()

if __name__ == "__main__":
    main()
