import subprocess
import sys
import os

def install_dependencies():
    dependencies = ["opencv-python", "customtkinter", "face-recognition", "pillow"]
    
    print("🚀 Checking system requirements...")
    
    for dep in dependencies:
        try:
            __import__(dep.split('-')[0]) # Quick check if library is installed
            print(f"✅ {dep} is already installed.")
        except ImportError:
            print(f"📦 Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully.")

    print("\n🎉 All systems go! Launching Attendance AI...")
    subprocess.run([sys.executable, "login.py"])

if __name__ == "__main__":
    install_dependencies()