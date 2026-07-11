import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class AttendanceViewer:
    def __init__(self, window):
        self.window = window
        self.window.title("AI Attendance - Data Viewer")
        self.window.geometry("900x600")
        
        # --- STYLING THE TABLE (Treeview) FOR DARK MODE ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2B302B", 
                        foreground="white", 
                        rowheight=30, 
                        fieldbackground="#2B302B",
                        font=("Helvetica", 12))
        style.map('Treeview', background=[('selected', '#2E7D32')])
        style.configure("Treeview.Heading", 
                        background="#1E1E1E", 
                        foreground="white", 
                        font=("Helvetica", 13, "bold"))
        
        # --- TOP CONTROLS FRAME ---
        self.top_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)
        
        self.title_lbl = ctk.CTkLabel(self.top_frame, text="Today's Attendance", font=("Helvetica", 24, "bold"), text_color="#4CAF50")
        self.title_lbl.pack(side="left", padx=10)
        
        # Class Filter Dropdown
        self.filter_var = ctk.StringVar(value="All Classes")
        self.classes_list = ["All Classes", "10-A", "10-B", "11-Science", "11-Commerce", "12-Science", "12-Arts"]
        self.class_filter = ctk.CTkOptionMenu(self.top_frame, values=self.classes_list, variable=self.filter_var, command=self.load_data)
        self.class_filter.pack(side="left", padx=20)
        
        # Export Button
        self.export_btn = ctk.CTkButton(self.top_frame, text="📥 Export to CSV", font=("Helvetica", 14, "bold"), 
                                        fg_color="#1976D2", hover_color="#1565C0", command=self.export_csv)
        self.export_btn.pack(side="right", padx=10)
        
        # Refresh Button
        self.refresh_btn = ctk.CTkButton(self.top_frame, text="🔄 Refresh", font=("Helvetica", 14, "bold"), 
                                         fg_color="#2E7D32", hover_color="#1B5E20", command=self.load_data)
        self.refresh_btn.pack(side="right", padx=10)
        
        # --- TABLE FRAME ---
        self.table_frame = ctk.CTkFrame(self.window)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        self.tree_scroll = tk.Scrollbar(self.table_frame)
        self.tree_scroll.pack(side="right", fill="y")
        
        # The actual Table
        self.tree = ttk.Treeview(self.table_frame, yscrollcommand=self.tree_scroll.set, selectmode="extended")
        self.tree.pack(fill="both", expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        # Define Columns
        self.tree['columns'] = ("ID", "Name", "Roll No", "Class", "Time", "Smiled")
        self.tree.column("#0", width=0, stretch=tk.NO) # Hide default first column
        self.tree.column("ID", anchor="center", width=80)
        self.tree.column("Name", anchor="w", width=200)
        self.tree.column("Roll No", anchor="center", width=100)
        self.tree.column("Class", anchor="center", width=120)
        self.tree.column("Time", anchor="center", width=120)
        self.tree.column("Smiled", anchor="center", width=100)
        
        # Define Headings
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Roll No", text="Roll No")
        self.tree.heading("Class", text="Class")
        self.tree.heading("Time", text="Check-In Time")
        self.tree.heading("Smiled", text="Smiled?")
        
        # Load the data immediately upon opening
        self.load_data()

    def load_data(self, event=None):
        """Fetches today's attendance from the database and updates the table."""
        # Clear the current table data
        for record in self.tree.get_children():
            self.tree.delete(record)
            
        today_str = datetime.now().strftime("%d-%m-%Y")
        selected_class = self.filter_var.get()
        
        try:
            conn = sqlite3.connect("database/attendance_system.db")
            cursor = conn.cursor()
            
            # INNER JOIN combines the students table and the attendance table
            if selected_class == "All Classes":
                cursor.execute('''
                    SELECT s.student_id, s.name, s.roll_no, s.class, a.time, a.smiled 
                    FROM attendance a 
                    JOIN students s ON a.student_id = s.student_id 
                    WHERE a.date = ?
                    ORDER BY a.time DESC
                ''', (today_str,))
            else:
                cursor.execute('''
                    SELECT s.student_id, s.name, s.roll_no, s.class, a.time, a.smiled 
                    FROM attendance a 
                    JOIN students s ON a.student_id = s.student_id 
                    WHERE a.date = ? AND s.class = ?
                    ORDER BY a.time DESC
                ''', (today_str, selected_class))
                
            records = cursor.fetchall()
            
            # Insert the fetched data into the Treeview
            for count, record in enumerate(records):
                self.tree.insert(parent='', index='end', iid=count, text='', values=record)
                
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load data: {e}")

    def export_csv(self):
        """Exports the data currently visible in the table to a CSV file."""
        if len(self.tree.get_children()) == 0:
            messagebox.showwarning("Empty", "There is no data to export!")
            return
            
        # Ask the user where they want to save the file
        today_str = datetime.now().strftime("%d-%m-%Y")
        selected_class = self.filter_var.get()
        default_filename = f"Attendance_{selected_class}_{today_str}.csv"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            title="Save Attendance Report",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Write the headers
                    writer.writerow(["Student ID", "Full Name", "Roll No", "Class", "Check-In Time", "Smiled?"])
                    
                    # Write the rows
                    for row_id in self.tree.get_children():
                        row_data = self.tree.item(row_id)['values']
                        writer.writerow(row_data)
                        
                messagebox.showinfo("Success", f"Data successfully exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = AttendanceViewer(root)
    root.mainloop()