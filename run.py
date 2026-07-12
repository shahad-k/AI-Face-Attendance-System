import os
import time
import threading
import webbrowser

def start_server():
    # Start the Flask app
    os.system("python app.py")

if __name__ == "__main__":
    print("=========================================")
    print("    🚀 Starting AI Attendance System")
    print("=========================================")
    
    # Start the Flask server in a background thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("\n[1] Starting Local AI Server...")
    print("[2] Waiting for server to initialize...")
    time.sleep(3) # Wait for Flask to boot up
    
    print("[3] Opening your Web Browser...")
    webbrowser.open("http://127.0.0.1:5000")
    
    print("\n✅ System is now running!")
    print("Keep this terminal window open while using the system.")
    print("To stop the server, just close this window.")
    print("=========================================\n")
    
    # Keep the script running so the server stays alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
