import sys
import os
import threading
import webbrowser
import time
import tkinter as tk
from tkinter import messagebox

# If compiled with PyInstaller, append the temporary _MEIPASS folder to sys.path
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)

from app import app, init_db

def run_flask():
    """Runs the Flask web server."""
    try:
        init_db()
        # Run Flask server locally on port 5000 (debug=False, use_reloader=False)
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    except Exception as e:
        messagebox.showerror("Server Error", f"Failed to start Flask server:\n{str(e)}")
        sys.exit(1)

def open_browser():
    """Opens the local attendance portal in the default browser."""
    webbrowser.open("http://127.0.0.1:5000/")

def on_closing():
    """Confirms shutdown of the application."""
    if messagebox.askokcancel("Quit", "Do you want to stop the AI Attendance server and exit?"):
        root.destroy()
        os._exit(0)  # Use os._exit to kill all daemon threads immediately

if __name__ == "__main__":
    # Start the Flask web server in a daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Automatically open the browser after a short delay
    threading.Timer(1.5, open_browser).start()

    # Create UI for the Server Control Panel
    root = tk.Tk()
    root.title("AI Attendance Pro — Launcher")
    root.geometry("420x310")
    root.configure(bg="#0f172a") # Slate-900 background
    root.resizable(False, False)

    # Set application icon if available
    try:
        if os.path.exists("static/favicon.ico"):
            root.iconbitmap("static/favicon.ico")
    except Exception:
        pass

    # Load and display logo in the GUI
    try:
        from PIL import Image, ImageTk
        logo_path = "static/logo.jpg"
        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, "static/logo.jpg")
            
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((70, 70), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(root, image=photo, bg="#0f172a")
            logo_label.image = photo # keep reference
            logo_label.pack(pady=(15, 0))
    except Exception as e:
        print("Logo loading failed:", e)

    # Title Container
    title_frame = tk.Frame(root, bg="#0f172a")
    title_frame.pack(pady=(10, 5))

    title_label = tk.Label(
        title_frame, 
        text="🧠 AI Attendance Pro", 
        font=("Helvetica", 15, "bold"), 
        fg="#38bdf8", # Sky blue
        bg="#0f172a"
    )
    title_label.pack()

    # Status indicator container (shows running state with green dot)
    status_frame = tk.Frame(root, bg="#0f172a")
    status_frame.pack(pady=3)

    status_dot = tk.Canvas(status_frame, width=10, height=10, bg="#0f172a", highlightthickness=0)
    status_dot.create_oval(1, 1, 9, 9, fill="#22c55e", outline="#86efac") # Green indicator dot
    status_dot.pack(side=tk.LEFT, padx=(0, 6))

    status_label = tk.Label(
        status_frame, 
        text="Status: Server is running on port 5000", 
        font=("Helvetica", 9), 
        fg="#94a3b8", # Muted slate
        bg="#0f172a"
    )
    status_label.pack(side=tk.LEFT)

    # Launch portal Button
    open_btn = tk.Button(
        root, 
        text="🌐 Open Attendance Web App", 
        font=("Helvetica", 10, "bold"), 
        fg="#ffffff", 
        bg="#0284c7", # Ocean blue
        activebackground="#0369a1", 
        activeforeground="#ffffff", 
        borderwidth=0, 
        padx=18, 
        pady=7, 
        cursor="hand2",
        command=open_browser
    )
    open_btn.pack(pady=8)

    # Shutdown Server Button
    stop_btn = tk.Button(
        root, 
        text="🚪 Shutdown Server", 
        font=("Helvetica", 9), 
        fg="#ffffff", 
        bg="#dc2626", # Red
        activebackground="#b91c1c", 
        activeforeground="#ffffff", 
        borderwidth=0, 
        padx=12, 
        pady=4, 
        cursor="hand2",
        command=on_closing
    )
    stop_btn.pack(pady=3)

    # Low-contrast Copyright Footer
    footer_label = tk.Label(
        root, 
        text="AI Attendance Pro v1.0 | © Shahad K", 
        font=("Helvetica", 8), 
        fg="#475569", # Slate-600 (very subtle)
        bg="#0f172a"
    )
    footer_label.pack(side=tk.BOTTOM, pady=8)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
