"""
Comprehensive USSD Testing Tool for KASA
This script simulates the complete USSD user journey
"""

import requests
import time

BASE_URL = "http://localhost:8080"

class USSDTester:
    def __init__(self):
        self.session_id = "test_session_12345"
        self.service_code = "*123#"
        self.phone_number = "+254712345678"
        
    def send_ussd_request(self, text, description=""):
        """Send a USSD request and return the response"""
        data = {
            "sessionId": self.session_id,
            "serviceCode": self.service_code,
            "phoneNumber": self.phone_number,
            "text": text
        }
        
        print(f"\n📱 {description}")
        print(f"   User Input: '{text}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ussd",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                print(f"   📋 USSD Response:")
                print("   " + "─" * 40)
                # Format the response nicely
                response_lines = response.text.split('\n')
                for line in response_lines:
                    print(f"   │ {line}")
                print("   " + "─" * 40)
                return response.text
            else:
                print(f"   ❌ Error: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return None
    
    def test_complete_emergency_flow(self):
        """Test a complete emergency alert flow"""
        print("\n🚨 TESTING COMPLETE EMERGENCY ALERT FLOW")
        print("=" * 60)
        
        # Step 1: Main menu
        response = self.send_ussd_request("", "User dials *123#")
        if not response or not response.startswith("CON"):
            print("❌ Failed to get main menu")
            return False
        
        time.sleep(1)
        
        # Step 2: Select emergency alert
        response = self.send_ussd_request("1", "User selects '1' - Send Emergency Alert")
        if not response or "Fire Emergency" not in response:
            print("❌ Failed to get emergency menu")
            return False
        
        time.sleep(1)
        
        # Step 3: Select fire emergency
        response = self.send_ussd_request("1*1", "User selects '1' - Fire Emergency")
        if not response or "Confirm sending" not in response:
            print("❌ Failed to get confirmation menu")
            return False
        
        time.sleep(1)
        
        # Step 4: Confirm alert
        response = self.send_ussd_request("1*1*1", "User selects '1' - Yes, Send Alert")
        if not response or "alert has been sent" not in response:
            print("❌ Failed to send alert")
            return False
        
        print("\n✅ COMPLETE EMERGENCY FLOW TEST PASSED!")
        return True
    
    def test_system_status_flow(self):
        """Test system status check flow"""
        print("\n📊 TESTING SYSTEM STATUS FLOW")
        print("=" * 60)
        
        # Main menu -> System status
        self.send_ussd_request("", "User dials *123#")
        time.sleep(0.5)
        
        response = self.send_ussd_request("2", "User selects '2' - View System Status")
        if response and "System is operational" in response:
            print("✅ SYSTEM STATUS TEST PASSED!")
            return True
        else:
            print("❌ SYSTEM STATUS TEST FAILED!")
            return False
    
    def test_help_flow(self):
        """Test help menu flow"""
        print("\n❓ TESTING HELP FLOW")
        print("=" * 60)
        
        # Main menu -> Help
        self.send_ussd_request("", "User dials *123#")
        time.sleep(0.5)
        
        response = self.send_ussd_request("3", "User selects '3' - Help")
        if response and "KASA Help" in response:
            # Test back navigation
            time.sleep(0.5)
            response = self.send_ussd_request("3*0", "User selects '0' - Back to Main Menu")
            if response and "Welcome to KASA" in response:
                print("✅ HELP FLOW TEST PASSED!")
                return True
        
        print("❌ HELP FLOW TEST FAILED!")
        return False
    
    def test_error_scenarios(self):
        """Test invalid input scenarios"""
        print("\n⚠️ TESTING ERROR SCENARIOS")
        print("=" * 60)
        
        # Test invalid main menu option
        self.send_ussd_request("", "User dials *123#")
        time.sleep(0.5)
        
        response = self.send_ussd_request("9", "User selects invalid option '9'")
        if response and "Invalid option" in response:
            print("✅ Invalid option handling works!")
        else:
            print("❌ Invalid option handling failed!")
        
        time.sleep(0.5)
        
        # Test invalid emergency type
        self.send_ussd_request("1", "User goes to emergency menu")
        time.sleep(0.5)
        
        response = self.send_ussd_request("1*9", "User selects invalid emergency type '9'")
        if response and "Invalid emergency type" in response:
            print("✅ Invalid emergency type handling works!")
            return True
        else:
            print("❌ Invalid emergency type handling failed!")
            return False
    
    def run_all_tests(self):
        """Run the complete USSD test suite"""
        print("🚀 KASA USSD TESTING SUITE")
        print("=" * 60)
        print(f"📱 Testing Phone: {self.phone_number}")
        print(f"📞 Service Code: {self.service_code}")
        print(f"🔖 Session ID: {self.session_id}")
        
        results = []
        
        # Run all test scenarios
        results.append(self.test_complete_emergency_flow())
        results.append(self.test_system_status_flow())
        results.append(self.test_help_flow())
        results.append(self.test_error_scenarios())
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        test_names = [
            "Emergency Alert Flow",
            "System Status Flow", 
            "Help Menu Flow",
            "Error Scenarios"
        ]
        
        for i, (test_name, result) in enumerate(zip(test_names, results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:.<30} {status}")
        
        print("=" * 60)
        print(f"📈 OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL USSD TESTS PASSED! The USSD system is working perfectly!")
        else:
            print("⚠️ Some tests failed. Please check the USSD implementation.")

def main():
    """Main function to run USSD tests"""
    print("🔌 Checking if KASA server is running...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ KASA server is running!")
        else:
            print("❌ KASA server is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to KASA server: {e}")
        print("💡 Make sure to run: python main.py")
        return
    
    # Run the tests
    tester = USSDTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
