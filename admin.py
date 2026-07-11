import customtkinter as ctk
import tkinter.ttk as ttk
import sqlite3
from datetime import datetime
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

# --- UI SETTINGS ---
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("green")

class AdminPanel:
    def __init__(self, window):
        self.window = window
        self.window.title("SchoolSecure - Admin Portal")
        self.window.geometry("1200x750")
        
        # Safely handle the window closing to prevent CustomTkinter errors
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # --- LOGIN SCREEN ---
        self.login_frame = ctk.CTkFrame(self.window, corner_radius=15, fg_color="#F5F5F0")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.title_lbl = ctk.CTkLabel(self.login_frame, text="🔒 Admin Portal", font=("Helvetica", 24, "bold"), text_color="#2E7D32")
        self.title_lbl.pack(pady=(30, 10), padx=50)
        
        self.pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter Password", show="*", width=200, height=40)
        self.pass_entry.pack(pady=20, padx=50)
        
        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", font=("Helvetica", 16, "bold"), 
                                       fg_color="#4CAF50", hover_color="#388E3C", height=40, command=self.verify_login)
        self.login_btn.pack(pady=(0, 30), padx=50)

    def on_closing(self):
        """Kills all background loops safely to prevent terminal crash errors."""
        plt.close('all')
        self.window.quit()
        sys.exit(0)

    def verify_login(self):
        if self.pass_entry.get() == "admin":
            self.login_frame.destroy()
            self.build_main_layout()
            self.show_dashboard() # Show the dashboard by default
        else:
            messagebox.showerror("Access Denied", "Incorrect Password!")

    def build_main_layout(self):
        """Builds the persistent sidebar and the dynamic content area."""
        self.main_container = ctk.CTkFrame(self.window, fg_color="#F5F5F0") 
        self.main_container.pack(fill="both", expand=True)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0, fg_color="#2B302B")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_lbl = ctk.CTkLabel(self.sidebar, text="🏫 SchoolSecure", font=("Helvetica", 22, "bold"), text_color="#FFFFFF")
        logo_lbl.pack(pady=(30, 30))

        # Sidebar Navigation Buttons
        btn_font = ("Helvetica", 16)
        ctk.CTkButton(self.sidebar, text="📊 Dashboard", font=btn_font, fg_color="#4CAF50", anchor="w", 
                      command=self.show_dashboard).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="👥 Students", font=btn_font, fg_color="transparent", hover_color="#4CAF50", anchor="w", 
                      command=self.show_students).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="📝 Reports", font=btn_font, fg_color="transparent", hover_color="#4CAF50", anchor="w", 
                      command=self.show_reports).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="🚪 Logout", font=btn_font, fg_color="#D32F2F", hover_color="#B71C1C", 
                      anchor="w", command=self.on_closing).pack(side="bottom", pady=30, padx=20, fill="x")

        # --- CONTENT AREA (Where pages will load) ---
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)

    def clear_content(self):
        """Destroys whatever is currently in the content area so we can load a new page."""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ==========================================
    # PAGE 1: DASHBOARD
    # ==========================================
    def show_dashboard(self):
        self.clear_content()

        header = ctk.CTkLabel(self.content_area, text=f"Daily Attendance Overview - {datetime.now().strftime('%b %d, %Y')}", 
                              font=("Helvetica", 24, "bold"), text_color="#333333")
        header.pack(anchor="w", pady=(0, 20))

        self.charts_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.charts_frame.pack(fill="x", pady=(0, 20))

        self.build_pie_chart()

        self.table_frame = ctk.CTkFrame(self.content_area, corner_radius=15, fg_color="#FFFFFF")
        self.table_frame.pack(fill="both", expand=True)

        table_title = ctk.CTkLabel(self.table_frame, text="Today's Logs", font=("Helvetica", 18, "bold"), text_color="#333333")
        table_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.build_data_table()

    def get_attendance_data(self):
        today = datetime.now().strftime("%d-%m-%Y")
        total_students = 0
        present_students = 0
        logs = []

        try:
            conn = sqlite3.connect("database/attendance_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]

            cursor.execute("""
                SELECT students.roll_no, students.name, students.class, attendance.time, students.gender 
                FROM attendance 
                JOIN students ON attendance.student_id = students.student_id 
                WHERE attendance.date = ?
                ORDER BY attendance.time DESC
            """, (today,))
            
            logs = cursor.fetchall()
            present_students = len(logs)
            conn.close()
        except Exception as e:
            print(f"Database Error: {e}")

        absent_students = total_students - present_students
        return total_students, present_students, absent_students, logs

    def build_pie_chart(self):
        total, present, absent, _ = self.get_attendance_data()

        chart_card = ctk.CTkFrame(self.charts_frame, corner_radius=15, fg_color="#FFFFFF")
        chart_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        lbl = ctk.CTkLabel(chart_card, text="Today's Attendance Status", font=("Helvetica", 16, "bold"), text_color="#333333")
        lbl.pack(anchor="w", padx=20, pady=10)

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        
        if total == 0:
            ax.text(0.5, 0.5, "No Students Registered", ha='center', va='center', fontsize=12)
            ax.axis('off')
        else:
            labels = ['Present', 'Absent']
            sizes = [present, absent]
            colors = ['#81C784', '#E57373'] 
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', 
                                              startangle=90, pctdistance=0.85, textprops={'fontsize': 10})
            
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig.gca().add_artist(centre_circle)
            ax.axis('equal')  

        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def build_data_table(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#FFFFFF", foreground="#333333", rowheight=35, 
                        fieldbackground="#FFFFFF", bordercolor="#EEEEEE", borderwidth=0, font=("Helvetica", 12))
        style.map('Treeview', background=[('selected', '#C8E6C9')])
        style.configure("Treeview.Heading", background="#F5F5F0", foreground="#333333", font=("Helvetica", 13, "bold"), borderwidth=0)

        columns = ("Roll No", "Name", "Class", "Gender", "Time In", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(fill="both", expand=True, padx=20, pady=15)

        _, _, _, logs = self.get_attendance_data()
        for log in logs:
            roll_no, name, student_class, time_in, gender = log
            self.tree.insert("", "end", values=(roll_no, name, student_class, gender, time_in, "✅ Present"))

    # ==========================================
    # PAGE 2: STUDENTS
    # ==========================================
    def show_students(self):
        self.clear_content()
        
        header = ctk.CTkLabel(self.content_area, text="👥 Student Database", font=("Helvetica", 24, "bold"), text_color="#333333")
        header.pack(anchor="w", pady=(0, 20))
        
        info = ctk.CTkLabel(self.content_area, text="This page will contain the full list of registered students and their details.", 
                            font=("Helvetica", 16), text_color="#666666")
        info.pack(anchor="w")

    # ==========================================
    # PAGE 3: REPORTS
    # ==========================================
    def show_reports(self):
        self.clear_content()
        
        header = ctk.CTkLabel(self.content_area, text="📝 Attendance Reports", font=("Helvetica", 24, "bold"), text_color="#333333")
        header.pack(anchor="w", pady=(0, 20))
        
        info = ctk.CTkLabel(self.content_area, text="This page will allow you to download monthly Excel sheets.", 
                            font=("Helvetica", 16), text_color="#666666")
        info.pack(anchor="w")

if __name__ == "__main__":
    root = ctk.CTk()
    app = AdminPanel(root)
    root.mainloop()