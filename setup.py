import subprocess
import sys
import os

def install_dependencies():
    """Install dependencies with proper version constraints for Render deployment"""
    try:
        print("🚀 Starting dependency installation for Render deployment...")
        
        # Upgrade pip first
        print("📦 Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install wheel for better package compilation
        print("🛠️ Installing build tools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "wheel", "setuptools"])
        
        # Uninstall conflicting versions
        print("🧹 Cleaning up existing packages...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "numpy", "scipy"], 
                      capture_output=True)
        
        # Install compatible versions in order
        print("📚 Installing core dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy==1.10.1"])
        
        # Install requirements
        print("📋 Installing requirements...")
        if os.path.exists("requirements.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            print("⚠️ requirements.txt not found, installing core packages...")
            core_packages = [
                "fastapi==0.104.1",
                "uvicorn[standard]==0.24.0",
                "pydantic==2.5.0",
                "python-dotenv==1.0.0",
                "requests==2.31.0",
                "PyMuPDF==1.23.26"
            ]
            for package in core_packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ Dependencies installed successfully!")
        
        # Verify installation
        print("🔍 Verifying installation...")
        try:
            import fastapi
            import uvicorn
            import pydantic
            print("✅ Core packages verified!")
        except ImportError as e:
            print(f"⚠️ Import warning: {e}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_render_readiness():
    """Check if the application is ready for Render deployment"""
    print("\n🔍 Checking Render deployment readiness...")
    
    checks = []
    
    # Check for required files
    required_files = ["app.py", "requirements.txt", "render.yaml"]
    for file in required_files:
        if os.path.exists(file):
            checks.append(f"✅ {file} exists")
        else:
            checks.append(f"❌ {file} missing")
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv("GEMINI_API_KEY"):
        checks.append("✅ GEMINI_API_KEY configured")
    else:
        checks.append("⚠️ GEMINI_API_KEY not set in .env")
    
    if os.getenv("API_KEY"):
        checks.append("✅ API_KEY configured")
    else:
        checks.append("⚠️ API_KEY not set in .env")
    
    # Print results
    for check in checks:
        print(f"   {check}")
    
    return all("✅" in check for check in checks)

if __name__ == "__main__":
    success = install_dependencies()
    if success:
        ready = check_render_readiness()
        print(f"\n🎯 Render deployment ready: {'Yes' if ready else 'No'}")
    exit(0 if success else 1)
