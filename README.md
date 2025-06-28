# KASA - Local Alert & Notification System

KASA is a FastAPI-based backend system for sending SMS alerts and handling USSD menu interactions using Africa's Talking services.

## Features

- 🚨 **SMS Alerts**: Send emergency alerts to multiple recipients
- 📱 **USSD Menu**: Interactive USSD interface for emergency reporting
- 🔐 **Environment Configuration**: Secure API key management
- ✅ **Request Validation**: Pydantic-based input validation
- 📊 **Health Monitoring**: System health check endpoints
- 🛡️ **Error Handling**: Comprehensive error handling and logging

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the `.env` file and add your Africa's Talking credentials:

```bash
# .env file
AFRICAS_TALKING_USERNAME=your_username_here
AFRICAS_TALKING_API_KEY=your_api_key_here
AFRICAS_TALKING_SENDER_ID=KASA
```

### 3. Get Africa's Talking Credentials

1. Sign up at [Africa's Talking](https://africastalking.com/)
2. Go to your dashboard and get your username and API key
3. Add them to your `.env` file

### 4. Run the Application

```bash
# Development mode
uvicorn main:app --reload

# Production mode
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Root Endpoint
```
GET /
Response: {"message": "Welcome to KASA"}
```

### Send SMS Alert
```
POST /send-alert
Content-Type: application/json

{
    "message": "Emergency: Fire reported at Building A",
    "recipients": ["+254712345678", "+254798765432"]
}
```

### USSD Handler
```
POST /ussd
Content-Type: application/x-www-form-urlencoded

sessionId=session123&serviceCode=*123#&phoneNumber=%2B254712345678&text=1*2*1
```

### Health Check
```
GET /health
Response: {
    "status": "healthy",
    "service": "KASA Alert System",
    "timestamp": "2025-06-27",
    "africas_talking": "configured"
}
```

## USSD Menu Structure

```
Main Menu:
├── 1. Send Emergency Alert
│   ├── 1. Fire Emergency
│   ├── 2. Medical Emergency
│   ├── 3. Security Alert
│   └── 4. Natural Disaster
├── 2. View System Status
├── 3. Help
└── 0. Exit
```

## Usage Examples

### Sending SMS Alert via API

```python
import requests

response = requests.post('http://localhost:8000/send-alert', json={
    "message": "Emergency: Fire at Main Street",
    "recipients": ["+254712345678", "+254798765432"]
})

print(response.json())
```

### Testing USSD Flow

```bash
# Simulate USSD request (using curl)
curl -X POST http://localhost:8000/ussd \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=123&serviceCode=*123#&phoneNumber=%2B254712345678&text="
```

## Error Handling

The API includes comprehensive error handling:

- **Validation Errors**: Invalid phone numbers, empty messages
- **API Errors**: Africa's Talking service issues
- **System Errors**: Database or network connectivity issues

## Security Considerations

- API keys are stored in environment variables
- Input validation prevents malicious payloads
- Phone number format validation
- Rate limiting (implement as needed)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (create test files as needed)
pytest
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## Production Deployment

1. Set up proper environment variables
2. Use a production WSGI server (e.g., Gunicorn)
3. Implement proper logging and monitoring
4. Set up rate limiting and security headers
5. Use HTTPS in production

```bash
# Example production command
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### Common Issues

1. **"Africa's Talking credentials not found"**
   - Check your `.env` file exists and has correct variable names
   - Ensure you've set the credentials in your Africa's Talking dashboard

2. **"Failed to send SMS"**
   - Verify your Africa's Talking account has sufficient credit
   - Check phone number formats (must include country code)
   - Verify your API key has SMS permissions

3. **USSD not working**
   - Ensure your USSD code is properly configured in Africa's Talking dashboard
   - Check that the webhook URL points to your `/ussd` endpoint

## License

This project is open source and available under the MIT License.
