import subprocess
import sys
import os

def fix_dependencies():
    """Install compatible versions of all dependencies for Render deployment"""
    commands = [
        # Upgrade pip first
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        
        # Uninstall problematic packages
        [sys.executable, "-m", "pip", "uninstall", "-y", "langchain", "langchain-core", "langchain-community", "langchain-google-genai", "numpy", "scipy"],
        
        # Install core dependencies first with specific versions
        [sys.executable, "-m", "pip", "install", "numpy==1.24.3"],
        [sys.executable, "-m", "pip", "install", "scipy==1.10.1"],
        
        # Install LangChain with specific compatible versions
        [sys.executable, "-m", "pip", "install", "langchain-core==0.1.52"],
        [sys.executable, "-m", "pip", "install", "langchain==0.1.20"],
        [sys.executable, "-m", "pip", "install", "langchain-community==0.0.38"],
        [sys.executable, "-m", "pip", "install", "langchain-google-genai==1.0.3"],
        
        # Install Google AI dependencies
        [sys.executable, "-m", "pip", "install", "google-generativeai==0.3.2"],
        
        # Install other core requirements
        [sys.executable, "-m", "pip", "install", "fastapi==0.104.1"],
        [sys.executable, "-m", "pip", "install", "uvicorn[standard]==0.24.0"],
        [sys.executable, "-m", "pip", "install", "pydantic==2.5.0"],
        [sys.executable, "-m", "pip", "install", "python-dotenv==1.0.0"],
        [sys.executable, "-m", "pip", "install", "requests==2.31.0"],
        [sys.executable, "-m", "pip", "install", "PyMuPDF==1.23.26"],
        [sys.executable, "-m", "pip", "install", "nltk==3.8.1"],
        [sys.executable, "-m", "pip", "install", "faiss-cpu==1.7.4"],
        [sys.executable, "-m", "pip", "install", "python-multipart==0.0.6"],
        
        # Final requirements install to catch any missing dependencies
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--force-reinstall", "--no-deps"]
    ]
    
    for cmd in commands:
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"Warning: Command failed with return code {result.returncode}")
                print(f"STDERR: {result.stderr}")
            else:
                print(f"Success: {result.stdout}")
        except subprocess.TimeoutExpired:
            print(f"Warning: Command timed out: {' '.join(cmd)}")
            continue
        except subprocess.CalledProcessError as e:
            print(f"Warning: Command failed: {e}")
            continue
        except Exception as e:
            print(f"Error running command: {e}")
            continue
    
    print("Dependencies installation completed!")
    
    # Verify critical imports
    try:
        import langchain
        import langchain_google_genai
        import faiss
        import fastapi
        print("✅ All critical dependencies verified successfully!")
        return True
    except ImportError as e:
        print(f"❌ Critical dependency missing: {e}")
        return False

if __name__ == "__main__":
    success = fix_dependencies()
    exit(0 if success else 1)
