#!/usr/bin/env python3
"""
KASA Easy Cloud Deployment Script
Helps you deploy KASA to various cloud platforms
"""

import os
import subprocess
import sys

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_git():
    """Check if git is available"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except:
        print("❌ Git is not installed. Please install Git first.")
        return False

def deploy_to_replit():
    """Guide for Replit deployment"""
    print_header("🔥 Deploy to Replit (Easiest Option)")
    
    print("📋 Steps to deploy to Replit:")
    print("1. Go to: https://replit.com/")
    print("2. Click 'Create Repl'")
    print("3. Choose 'Python' template")
    print("4. Upload your KASA files:")
    print("   - main.py")
    print("   - requirements.txt")
    print("   - .env")
    print("   - All other files from this folder")
    print("\n5. In Replit console, run:")
    print("   pip install -r requirements.txt")
    print("\n6. Click 'Run' or execute:")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8080")
    print("\n7. Your callback URL will be:")
    print("   https://your-repl-name.username.repl.co/ussd")
    
    print("\n✅ Replit automatically handles HTTPS and gives you a public URL!")

def deploy_to_railway():
    """Guide for Railway deployment"""
    print_header("🚂 Deploy to Railway")
    
    print("📋 Steps to deploy to Railway:")
    print("1. Go to: https://railway.app/")
    print("2. Sign up with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Or click 'Deploy Now' and upload files")
    print("\n5. Railway will auto-detect Python and deploy")
    print("6. Your callback URL will be:")
    print("   https://your-app.railway.app/ussd")
    
    print("\n🎯 Alternative - Railway CLI:")
    print("1. Install: npm install -g @railway/cli")
    print("2. Run: railway login")
    print("3. Run: railway new")
    print("4. Run: railway up")

def deploy_to_render():
    """Guide for Render deployment"""
    print_header("🎨 Deploy to Render")
    
    print("📋 Steps to deploy to Render:")
    print("1. Go to: https://render.com/")
    print("2. Sign up (free account)")
    print("3. Click 'New Web Service'")
    print("4. Connect GitHub repo or upload files")
    print("\n5. Configure build settings:")
    print("   Build Command: pip install -r requirements.txt")
    print("   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT")
    print("\n6. Add environment variables:")
    print("   AFRICAS_TALKING_USERNAME=your_username")
    print("   AFRICAS_TALKING_API_KEY=your_api_key")
    print("\n7. Your callback URL will be:")
    print("   https://your-app.onrender.com/ussd")

def deploy_to_heroku():
    """Deploy to Heroku with CLI"""
    print_header("☁️ Deploy to Heroku")
    
    if not check_git():
        return
    
    print("📋 Heroku deployment steps:")
    print("1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
    print("2. I'll help you deploy from here...")
    
    app_name = input("\nEnter your desired app name (lowercase, no spaces): ").strip()
    if not app_name:
        app_name = "kasa-alert-system"
    
    try:
        # Initialize git if not already
        if not os.path.exists('.git'):
            print("🔧 Initializing git repository...")
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial KASA deployment'], check=True)
        
        print(f"🚀 Creating Heroku app: {app_name}")
        subprocess.run(['heroku', 'create', app_name], check=True)
        
        print("🔐 Setting environment variables...")
        # You'll need to set these manually or get them from user
        print("⚠️ Remember to set your environment variables:")
        print(f"   heroku config:set AFRICAS_TALKING_USERNAME=your_username -a {app_name}")
        print(f"   heroku config:set AFRICAS_TALKING_API_KEY=your_api_key -a {app_name}")
        
        print("📦 Deploying to Heroku...")
        subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
        
        print(f"✅ Deployment complete!")
        print(f"🌐 Your callback URL: https://{app_name}.herokuapp.com/ussd")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print("💡 Make sure Heroku CLI is installed and you're logged in")
        print("   Run: heroku login")

def create_zip_package():
    """Create a ZIP package for manual upload"""
    print_header("📦 Create ZIP Package for Manual Upload")
    
    try:
        import zipfile
        
        zip_name = "kasa-deployment.zip"
        
        files_to_include = [
            'main.py',
            'requirements.txt',
            '.env',
            'Procfile',
            'vercel.json',
            'sample_users.csv',
            'USER_MANAGEMENT_GUIDE.md',
            'ALTERNATIVE_PLATFORMS.md'
        ]
        
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            for file in files_to_include:
                if os.path.exists(file):
                    zipf.write(file)
                    print(f"✅ Added {file}")
        
        print(f"\n📦 Created: {zip_name}")
        print("🌐 You can upload this to any platform:")
        print("   - Render.com")
        print("   - Railway.app") 
        print("   - Glitch.com")
        print("   - Vercel.com")
        
    except Exception as e:
        print(f"❌ Error creating ZIP: {e}")

def main():
    """Main deployment menu"""
    print("🚀 KASA Cloud Deployment Helper")
    print("Since ngrok isn't working, let's deploy to the cloud!")
    
    while True:
        print("\n" + "="*50)
        print("Choose your deployment platform:")
        print("="*50)
        print("1. 🔥 Replit (Easiest - No CLI needed)")
        print("2. 🚂 Railway (Modern - Good free tier)")
        print("3. 🎨 Render (Reliable - Good performance)")
        print("4. ☁️ Heroku (Classic - Auto deploy)")
        print("5. 📦 Create ZIP for manual upload")
        print("6. 📖 Show all options guide")
        print("7. 🚪 Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            deploy_to_replit()
        elif choice == '2':
            deploy_to_railway()
        elif choice == '3':
            deploy_to_render()
        elif choice == '4':
            deploy_to_heroku()
        elif choice == '5':
            create_zip_package()
        elif choice == '6':
            print("\n📖 See ALTERNATIVE_PLATFORMS.md for detailed guides")
        elif choice == '7':
            print("👋 Happy deploying!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
