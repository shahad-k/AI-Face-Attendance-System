import sqlite3

# Connect to the database
conn = sqlite3.connect("database/attendance_system.db")

try:
    # Add the new Gender column, defaulting to 'M' for old records
    conn.execute("ALTER TABLE students ADD COLUMN gender TEXT DEFAULT 'M'")
    print("✅ Database successfully upgraded! 'Gender' column added.")
except sqlite3.OperationalError:
    print("⚠️ Column already exists! You are good to go.")

conn.commit()
conn.close()