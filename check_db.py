import sqlite3

conn = sqlite3.connect("database/attendance_system.db")
cursor = conn.cursor()

# This command asks SQLite to list all columns in the table
cursor.execute("PRAGMA table_info(students)")
columns = cursor.fetchall()

print("Here are the actual columns in your 'students' table:")
for col in columns:
    # col[1] holds the actual name of the column
    print(f"- {col[1]}") 

conn.close()