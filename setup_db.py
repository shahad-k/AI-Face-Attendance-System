import sqlite3
import os

print("⏳ Script has started running...")

# Create a 'database' folder if it doesn't exist yet
db_folder = "database"
if not os.path.exists(db_folder):
    os.makedirs(db_folder)
    print("📁 Created 'database' folder.")
    
# Connect to SQLite database (it will create the file if it doesn't exist)
db_path = os.path.join(db_folder, "attendance_system.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔨 Building the tables...")

# 1. Create the Students Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    roll_no TEXT NOT NULL UNIQUE,
    class TEXT NOT NULL,
    age INTEGER,
    dob TEXT
)
''')

# 2. Create the Attendance Logs Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    smiled TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("🎉 Database initialized successfully at 'database/attendance_system.db'!")