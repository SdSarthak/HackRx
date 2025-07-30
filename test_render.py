#!/usr/bin/env python3
"""
Test script to verify Render deployment configuration.
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("✅ Python version is compatible with Render")
        return True
    else:
        print("❌ Python version may not be compatible. Recommended: Python 3.10+")
        return False

def check_requirements():
    """Check if requirements.txt is properly formatted."""
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.readlines()
        
        print(f"📦 Found {len(requirements)} packages in requirements.txt")
        
        # Check for critical packages
        critical_packages = ["fastapi", "uvicorn", "langchain", "google-generativeai"]
        found_packages = []
        
        for req in requirements:
            package_name = req.split("==")[0].split(">=")[0].split("<=")[0].strip()
            if package_name.lower() in [p.lower() for p in critical_packages]:
                found_packages.append(package_name)
        
        print(f"✅ Found critical packages: {', '.join(found_packages)}")
        return len(found_packages) >= 3
        
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_render_config():
    """Check if render.yaml configuration is valid."""
    try:
        with open("render.yaml", "r") as f:
            config = f.read()
        
        print("🔧 render.yaml configuration found")
        
        # Check for required fields
        required_fields = ["services", "type: web", "buildCommand", "startCommand"]
        missing_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields in render.yaml: {', '.join(missing_fields)}")
            return False
        else:
            print("✅ render.yaml configuration looks good")
            return True
            
    except FileNotFoundError:
        print("❌ render.yaml not found")
        return False

def check_environment_variables():
    """Check if environment variables are properly configured."""
    print("🔐 Checking environment variables...")
    
    env_vars = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "API_KEY": os.getenv("API_KEY"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
    }
    
    has_local_env = False
    for var, value in env_vars.items():
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}...")
            if var in ["GEMINI_API_KEY", "API_KEY"]:
                has_local_env = True
        else:
            print(f"ℹ️  {var}: Not set locally (configure in Render Dashboard)")
    
    if has_local_env:
        print("✅ Environment variables configured locally")
        return True
    else:
        print("ℹ️  Environment variables will be configured in Render Dashboard")
        return True  # This is acceptable for Render deployment

def check_app_structure():
    """Check if the application structure is correct for Render."""
    required_files = ["app.py", "requirements.txt", "render.yaml"]
    missing_files = []
    
    print("📁 Checking application structure...")
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
            missing_files.append(file)
    
    # Check for Heroku-specific files that should be removed
    heroku_files = ["Procfile", "runtime.txt"]
    for file in heroku_files:
        if os.path.exists(file):
            print(f"⚠️  {file} - Not needed for Render (consider removing)")
        else:
            print(f"✅ {file} - Correctly absent")
    
    return len(missing_files) == 0

def simulate_render_commands():
    """Simulate Render build and start commands."""
    print("🏗️  Simulating Render deployment commands...")
    
    # Check if uvicorn can import the app
    try:
        print("📦 Testing app import...")
        import app
        print("✅ App imports successfully")
        
        # Check if the app has the required endpoints
        if hasattr(app, 'app') and hasattr(app.app, 'routes'):
            routes = [route.path for route in app.app.routes if hasattr(route, 'path')]
            print(f"🛣️  Found routes: {routes}")
            
            required_routes = ["/", "/hackrx/run"]
            missing_routes = [route for route in required_routes if route not in routes]
            
            if missing_routes:
                print(f"❌ Missing required routes: {missing_routes}")
                return False
            else:
                print("✅ All required routes present")
                return True
        else:
            print("❌ App structure invalid")
            return False
            
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def run_render_readiness_check():
    """Run comprehensive Render readiness check."""
    print("🚀 Render Deployment Readiness Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Requirements", check_requirements),
        ("Render Config", check_render_config),
        ("Environment Variables", check_environment_variables),
        ("App Structure", check_app_structure),
        ("App Import", simulate_render_commands)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name}: PASSED")
            else:
                print(f"❌ {check_name}: FAILED")
        except Exception as e:
            print(f"❌ {check_name}: ERROR - {e}")
    
    print(f"\n{'='*50}")
    print(f"🎯 Render Readiness: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Your app is ready for Render deployment!")
        print("\n📝 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Create a new Blueprint in Render Dashboard")
        print("3. Connect your GitHub repository") 
        print("4. Set environment variables in Render")
        print("5. Deploy!")
    elif passed >= total * 0.8:
        print("⚠️  Your app is mostly ready, but has some issues to fix")
    else:
        print("❌ Your app needs significant changes before Render deployment")
    
    return passed == total

if __name__ == "__main__":
    success = run_render_readiness_check()
    exit(0 if success else 1)
