import os
import sys
import time
import threading
import webbrowser

def check_dependencies():
    """Check if required libraries are installed before starting."""
    missing = []
    try:
        import flask
    except ImportError:
        missing.append("flask")
        
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
        
    try:
        import face_recognition
    except ImportError:
        missing.append("face_recognition")
        
    return missing

def start_server():
    # Start the Flask app
    os.system(f'"{sys.executable}" app.py')

if __name__ == "__main__":
    print("=========================================")
    print("    🚀 AI Attendance System Setup")
    print("=========================================")
    print("[1] Checking system requirements...")
    
    missing_deps = check_dependencies()
    if missing_deps:
        print("\n❌ Error: Missing required Python libraries!")
        print("Please install them by running this exact command in your terminal:")
        print("\n    pip install -r requirements.txt\n")
        print("After installation is complete, run this script again.")
        print("=========================================")
        sys.exit(1)
        
    print("✅ All dependencies found!")
    print("\n[2] Starting Local AI Server...")
    
    # Start the Flask server in a background thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("[3] Waiting for server to initialize (3 seconds)...")
    time.sleep(3) # Wait for Flask to boot up
    
    print("[4] Opening your Web Browser...")
    webbrowser.open("http://127.0.0.1:5000")
    
    print("\n🎉 Success! The AI Attendance System is now running.")
    print("======================================================")
    print("⚠️  IMPORTANT: Do NOT close this black terminal window.")
    print("   Closing this window will shut down the server.")
    print("======================================================")
    
    # Keep the script running so the server stays alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
