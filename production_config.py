# production_config.py
"""
Production configuration for KASA USSD server
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8080))
    
    # Africa's Talking settings
    AT_USERNAME = os.getenv("AFRICAS_TALKING_USERNAME")
    AT_API_KEY = os.getenv("AFRICAS_TALKING_API_KEY")
    AT_SENDER_ID = os.getenv("AFRICAS_TALKING_SENDER_ID", "KASA")
    
    # USSD settings
    USSD_CODE = os.getenv("USSD_CODE", "*123#")
    
    # Security settings
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
    
    # Database (for production)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///kasa.db")

# Production startup
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    config = Config()
    uvicorn.run(
        app, 
        host=config.HOST, 
        port=config.PORT,
        access_log=True
    )
