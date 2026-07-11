import customtkinter as ctk
from tkinter import messagebox
import subprocess
import sys

# --- IMPORT CONFIG ---
from utils import config

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("green") 

class LoginScreen:
    def __init__(self, window):
        self.window = window
        self.window.title("AI Attendance - Teacher Login")
        self.window.geometry("500x450")
        
        # Center the window on the screen
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w // 2) - (500 // 2)
        y = (screen_h // 2) - (450 // 2)
        self.window.geometry(f"500x450+{x}+{y}")
        
        # --- UI DESIGN ---
        self.title_lbl = ctk.CTkLabel(self.window, text="System Login", font=("Helvetica", 28, "bold"), text_color=config.COLOR_SUCCESS)
        self.title_lbl.pack(pady=(40, 10))
        
        self.subtitle_lbl = ctk.CTkLabel(self.window, text="Please select your class and enter PIN", font=("Helvetica", 14), text_color="#A3B1A3")
        self.subtitle_lbl.pack(pady=(0, 30))
        
        # --- 1. GRAB PINS FROM CONFIG ---
        self.class_credentials = config.TEACHER_PINS
        
        self.class_var = ctk.StringVar(value="Select Class")
        # Automatically generate the dropdown list based on the config file
        self.classes = list(self.class_credentials.keys())
        
        self.class_dropdown = ctk.CTkOptionMenu(self.window, values=self.classes, variable=self.class_var, 
                                                width=250, height=40, font=("Helvetica", 15))
        self.class_dropdown.pack(pady=15)
        
        # PIN Entry
        self.pin_entry = ctk.CTkEntry(self.window, placeholder_text="Enter 4-Digit PIN", show="*", 
                                      width=250, height=40, font=("Helvetica", 15), justify="center")
        self.pin_entry.pack(pady=15)
        
        # Login Button
        self.login_btn = ctk.CTkButton(self.window, text="Start Camera Session", font=("Helvetica", 16, "bold"),
                                       width=250, height=45, fg_color="#2E7D32", hover_color="#1B5E20",
                                       command=self.verify_login)
        self.login_btn.pack(pady=30)
        
        self.window.bind('<Return>', lambda event: self.verify_login())

    def verify_login(self):
        selected_class = self.class_var.get()
        entered_pin = self.pin_entry.get()
        
        if selected_class == "Select Class":
            messagebox.showwarning("Error", "Please select a class from the dropdown.")
            return
            
        correct_pin = self.class_credentials.get(selected_class)
        
        if entered_pin == correct_pin:
            print(f"Login successful for {selected_class}.")
            self.window.destroy()  
            
            subprocess.run([sys.executable, "main.py", selected_class])
        else:
            messagebox.showerror("Access Denied", "Incorrect Teacher PIN for this class.")
            self.pin_entry.delete(0, 'end')

if __name__ == "__main__":
    root = ctk.CTk()
    app = LoginScreen(root)
    root.mainloop()