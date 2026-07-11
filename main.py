import cv2
import customtkinter as ctk
import tkinter as tk 
from tkinter import messagebox
from PIL import Image, ImageTk
import face_recognition
import pickle
import sqlite3
from datetime import datetime
import os
import subprocess
import sys

from utils import helpers
from birthday_ui import BirthdayPopup 

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("green") 

class AttendanceApp:
    def __init__(self, window):
        self.window = window
        self.window.title("AI Face Attendance System")
        self.window.geometry("1150x720")
        
        # --- CATCH THE SECRET CLASS FROM LOGIN ---
        # If launched from login.py, it grabs the class name. If launched directly, defaults to "All Classes".
        if len(sys.argv) > 1:
            self.current_class = sys.argv[1]
        else:
            self.current_class = "All Classes"
            
        self.marked_today = set()
        self.wished_today = set() 
        self.is_processing = False 

        try:
            with open("encodings.pickle", "rb") as f:
                data = pickle.load(f)
                self.known_encodings = data["encodings"]
                self.known_roll_nos = data["roll_nos"]
        except FileNotFoundError:
            messagebox.showerror("Error", "encodings.pickle not found! Run encode.py first.")
            self.window.destroy()
            return

        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

        # 1. Birthday Banner
        self.birthday_frame = ctk.CTkFrame(self.window, fg_color="#FFD700", corner_radius=0)
        self.birthday_lbl = ctk.CTkLabel(self.birthday_frame, text="", text_color="#000000", font=("Helvetica", 16, "bold"))
        self.birthday_lbl.pack(pady=5)
        self.check_birthdays()

        # 2. Main split container
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT SIDE: Camera
        self.left_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.camera_title = ctk.CTkLabel(self.left_frame, text="Live Camera", font=("Helvetica", 24, "bold"))
        self.camera_title.pack(pady=(0, 10))
        self.video_label = tk.Label(self.left_frame, bg="#1E1E1E", bd=0)
        self.video_label.pack(expand=True)

        # RIGHT SIDE: Dashboard
        self.right_frame = ctk.CTkFrame(self.main_frame, width=400, corner_radius=20, fg_color="#2B302B")
        self.right_frame.pack(side="right", fill="y")
        self.right_frame.pack_propagate(False)
        
        # --- UI UPDATE: SHOW CURRENT CLASS ---
        self.dashboard_title = ctk.CTkLabel(self.right_frame, text=f"Dashboard: {self.current_class}", 
                                            font=("Helvetica", 22, "bold"), text_color="#4CAF50")
        self.dashboard_title.pack(pady=(30, 20))

        self.profile_card = ctk.CTkFrame(self.right_frame, corner_radius=15, fg_color="#363C36")
        self.profile_card.pack(fill="x", padx=20, pady=10)
        self.info_lbl = ctk.CTkLabel(self.profile_card, text="Waiting for student...", font=("Helvetica", 16), justify="left")
        self.info_lbl.pack(pady=20, padx=20, anchor="w")

        self.status_lbl = ctk.CTkLabel(self.right_frame, text="You look good when you smile! 😊", 
                                       font=("Helvetica", 16, "italic"), text_color="#A3B1A3", wraplength=320)
        self.status_lbl.pack(pady=20, padx=20)

        self.reg_btn = ctk.CTkButton(self.right_frame, text="🔒 New Registration", font=("Helvetica", 15, "bold"), 
                                     corner_radius=10, height=45, fg_color="#2E7D32", hover_color="#1B5E20",
                                     command=self.open_registration)
        self.reg_btn.pack(side="bottom", pady=30, padx=20, fill="x")

        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def check_birthdays(self):
        birthday_students = helpers.check_and_update_birthdays()
        if birthday_students:
            names = ", ".join(birthday_students)
            banner_text = f"🎉 Hey everyone! Wish a very Happy Birthday to {names}! 🎂"
            self.birthday_lbl.configure(text=banner_text)
            self.birthday_frame.pack(fill="x")

    def reset_dashboard(self):
        self.info_lbl.configure(text="Waiting for student...", text_color="#FFFFFF")
        self.status_lbl.configure(text="You look good when you smile! 😊", text_color="#A3B1A3")
        self.is_processing = False  

    def process_dashboard_logic(self, roll_no, gray_frame, top, right, bottom, left):
        if self.is_processing: return 
        self.is_processing = True

        try:
            conn = sqlite3.connect("database/attendance_system.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT student_id, name, class, gender, age, dob FROM students WHERE roll_no = ?", (roll_no,))
            student = cursor.fetchone()
            
            if student:
                student_id, name, student_class, gender, student_age, dob = student
                
                # --- NEW: CLASS GATEKEEPER ---
                # Check if the student belongs to the currently logged-in class
                if self.current_class != "All Classes" and student_class != self.current_class:
                    self.info_lbl.configure(text=f"👤 Name: {name}\n\n🎓 Class: {student_class}\n\n🔢 Roll No: {roll_no}")
                    self.status_lbl.configure(text=f"❌ Wrong Room! This session is for {self.current_class}.", text_color="#FF5252")
                    conn.close()
                    self.window.after(3000, self.reset_dashboard)
                    return
                
                # --- ALREADY MARKED FLOW ---
                if roll_no in self.marked_today:
                    self.info_lbl.configure(text="")
                    if gender == 'FEMALE':
                        msg = "My lady... you already marked your presence. ✨"
                        color = "#FFB6C1"
                    else:
                        msg = "Bro, you already locked in your attendance. Go conquer the day! ⚡"
                        color = "#FFD700"
                    self.status_lbl.configure(text=msg, text_color=color)
                
                # --- FIRST TIME MARKING FLOW ---
                else:
                    self.info_lbl.configure(text=f"👤 Name: {name}\n\n🎓 Class: {student_class}\n\n🔢 Roll No: {roll_no}")
                    
                    top, bottom = max(0, top), min(gray_frame.shape[0], bottom)
                    left, right = max(0, left), min(gray_frame.shape[1], right)
                    face_roi = gray_frame[top:bottom, left:right]
                    is_smiling = "No"
                    
                    if face_roi.shape[0] > 0 and face_roi.shape[1] > 0:
                        smiles = self.smile_cascade.detectMultiScale(face_roi, scaleFactor=1.8, minNeighbors=20)
                        if len(smiles) > 0: is_smiling = "Yes"
                    
                    now = datetime.now()
                    date_str = now.strftime("%d-%m-%Y")
                    time_str = now.strftime("%H:%M:%S")
                    
                    cursor.execute("INSERT INTO attendance (student_id, date, time, smiled) VALUES (?, ?, ?, ?)", 
                                   (student_id, date_str, time_str, is_smiling))
                    conn.commit()
                    self.marked_today.add(roll_no)
                    self.status_lbl.configure(text="✅ Attendance Marked Successfully!", text_color="#4CAF50")
                    
                    # --- FOOLPROOF BIRTHDAY TRIGGER ---
                    # This replaces any spaces or slashes with dashes so it ALWAYS matches!
                    safe_dob = str(dob).replace(" ", "-").replace("/", "-")
                    
                    today_fmt1 = now.strftime("%m-%d") # Month-Day
                    today_fmt2 = now.strftime("%d-%m") # Day-Month
                    
                    if safe_dob and (today_fmt1 in safe_dob or today_fmt2 in safe_dob):
                        if roll_no not in self.wished_today:
                            self.wished_today.add(roll_no)
                            popup = BirthdayPopup(name, student_age)
                            self.window.wait_window(popup.window)
                    
            else:
                self.info_lbl.configure(text=f"⚠️ Unknown Record\nRoll No '{roll_no}' not in DB!")
                self.status_lbl.configure(text="❌ Save Failed", text_color="#FF5252")

            conn.close()
            self.window.after(2000, self.reset_dashboard)

        except Exception as e:
            self.status_lbl.configure(text=f"❌ Error: {e}", text_color="#FF5252")
            print(f"CRASH REPORT: {e}")
            self.window.after(2000, self.reset_dashboard)

    def open_registration(self):
        self.status_lbl.configure(text="Camera paused. Registration open...", text_color="#FFD700")
        self.cap.release()
        subprocess.run([sys.executable, "register.py"])
        with open("encodings.pickle", "rb") as f:
            data = pickle.load(f)
            self.known_encodings = data["encodings"]
            self.known_roll_nos = data["roll_nos"]
        self.cap = cv2.VideoCapture(0)
        self.reset_dashboard()

    def update_frame(self):
        if not self.cap.isOpened():
            self.window.after(1000, self.update_frame)
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1) 
            
            if not self.is_processing:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    top *= 4; right *= 4; bottom *= 4; left *= 4
                    matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
                    
                    if True in matches:
                        matched_idx = matches.index(True)
                        roll_no = self.known_roll_nos[matched_idx]
                        self.process_dashboard_logic(roll_no, gray_frame, top, right, bottom, left)
                        break 

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.window.after(10, self.update_frame)

    def on_close(self):
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = AttendanceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()