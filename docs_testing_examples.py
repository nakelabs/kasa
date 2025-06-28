"""
Demo script: How to test KASA API using FastAPI Docs
This script shows example payloads you can copy-paste into the docs interface
"""

import json

def print_section(title, emoji="🔧"):
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_json_example(title, data):
    print(f"\n📋 {title}:")
    print("```json")
    print(json.dumps(data, indent=2))
    print("```")

def main():
    print("🚀 KASA API TESTING EXAMPLES FOR FASTAPI DOCS")
    print("=" * 60)
    print("📖 Copy these examples into the docs interface at:")
    print("   http://localhost:8000/docs")
    print("=" * 60)
    
    # SMS Alert Examples
    print_section("SMS Alert Test Cases", "📱")
    
    # Basic SMS test
    basic_sms = {
        "message": "Test emergency alert from KASA docs interface",
        "recipients": ["+254711082972", "+254711082973"]
    }
    print_json_example("Basic SMS Alert (copy to /send-alert)", basic_sms)
    
    # Single recipient
    single_sms = {
        "message": "Fire emergency at Main Building - evacuate immediately!",
        "recipients": ["+254711082972"]
    }
    print_json_example("Single Recipient Alert", single_sms)
    
    # Longer message
    longer_sms = {
        "message": "KASA ALERT: Medical emergency reported. Emergency services notified. Please avoid the area.",
        "recipients": ["+254711082972", "+254711082973"]
    }
    print_json_example("Longer Message Alert", longer_sms)
    
    # USSD Examples
    print_section("USSD Test Cases", "📞")
    
    ussd_examples = [
        {
            "description": "Main Menu (Initial Dial)",
            "fields": {
                "sessionId": "docs_test_001",
                "serviceCode": "*123#",
                "phoneNumber": "+254712345678",
                "text": ""
            }
        },
        {
            "description": "Emergency Menu (User selects 1)",
            "fields": {
                "sessionId": "docs_test_001",
                "serviceCode": "*123#",
                "phoneNumber": "+254712345678",
                "text": "1"
            }
        },
        {
            "description": "Fire Emergency Confirmation (User selects 1*1)",
            "fields": {
                "sessionId": "docs_test_001",
                "serviceCode": "*123#",
                "phoneNumber": "+254712345678",
                "text": "1*1"
            }
        },
        {
            "description": "Send Fire Alert (User selects 1*1*1)",
            "fields": {
                "sessionId": "docs_test_001",
                "serviceCode": "*123#",
                "phoneNumber": "+254712345678",
                "text": "1*1*1"
            }
        },
        {
            "description": "System Status (User selects 2)",
            "fields": {
                "sessionId": "docs_test_002",
                "serviceCode": "*123#",
                "phoneNumber": "+254712345678",
                "text": "2"
            }
        },
        {
            "description": "Help Menu (User selects 3)",
            "fields": {
                "sessionId": "docs_test_003",
                "serviceCode": "*123#",
                "phoneNumber": "+254712345678",
                "text": "3"
            }
        }
    ]
    
    for example in ussd_examples:
        print(f"\n📋 {example['description']}:")
        print("Copy these values to the /ussd endpoint form:")
        for field, value in example['fields'].items():
            print(f"  {field}: {value}")
    
    # Error Test Cases
    print_section("Error Test Cases (Should Fail)", "⚠️")
    
    # Invalid phone number
    invalid_phone = {
        "message": "Test message",
        "recipients": ["254712345678"]  # Missing +
    }
    print_json_example("Invalid Phone Number (Missing +)", invalid_phone)
    
    # Empty message
    empty_message = {
        "message": "",
        "recipients": ["+254711082972"]
    }
    print_json_example("Empty Message (Should return 422)", empty_message)
    
    # No recipients
    no_recipients = {
        "message": "Test message",
        "recipients": []
    }
    print_json_example("No Recipients (Should return 422)", no_recipients)
    
    # Step-by-step instructions
    print_section("Step-by-Step Testing Instructions", "📋")
    
    instructions = [
        "1. Start KASA server: python main.py",
        "2. Open browser: http://localhost:8000/docs",
        "3. Test GET endpoints first:",
        "   - Click '/' endpoint → 'Try it out' → 'Execute'",
        "   - Click '/health' endpoint → 'Try it out' → 'Execute'",
        "   - Click '/test-credentials' → 'Try it out' → 'Execute'",
        "4. Test SMS Alert:",
        "   - Click '/send-alert' endpoint → 'Try it out'",
        "   - Replace example JSON with one from above",
        "   - Click 'Execute'",
        "   - Check response for success/error",
        "5. Test USSD:",
        "   - Click '/ussd' endpoint → 'Try it out'",
        "   - Fill form fields with examples above",
        "   - Click 'Execute'",
        "   - Check response starts with 'CON' or 'END'",
        "6. Test error cases to verify validation",
        "7. Check server logs in terminal for debugging"
    ]
    
    for instruction in instructions:
        print(f"   {instruction}")
    
    print_section("Expected Responses", "✅")
    
    responses = {
        "GET /": {"message": "Welcome to KASA"},
        "GET /health": {"status": "healthy", "service": "KASA Alert System"},
        "POST /send-alert (success)": {"message": "Alert processing completed", "successful_count": 2},
        "POST /ussd (main menu)": "CON Welcome to KASA - Local Alert System\\n1. Send Emergency Alert...",
        "POST /ussd (emergency)": "CON Select Emergency Type:\\n1. Fire Emergency...",
        "POST /ussd (confirmation)": "CON Confirm sending Fire Emergency?\\n1. Yes, Send Alert...",
        "POST /ussd (sent)": "END Fire Emergency alert has been sent!\\nEmergency contacts...",
    }
    
    for endpoint, response in responses.items():
        print(f"\n📋 {endpoint}:")
        if isinstance(response, dict):
            print(f"   {json.dumps(response, indent=2)}")
        else:
            print(f"   {response}")
    
    print("\n" + "=" * 60)
    print("🎉 Ready to test! Open http://localhost:8000/docs and start testing!")
    print("💡 Tip: Keep this terminal open to see server logs while testing")
    print("=" * 60)

if __name__ == "__main__":
    main()
