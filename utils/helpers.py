import sqlite3
from datetime import datetime

def check_and_update_birthdays():
    """
    Checks if today is any student's birthday, updates their age, 
    and returns a list of names to display on the UI banner.
    """
    conn = sqlite3.connect("database/attendance_system.db")
    cursor = conn.cursor()
    
    # Get today's date and year
    today = datetime.now()
    current_day_month = today.strftime("%d-%m") # Example: '15-06'
    current_year = today.year
    
    # Fetch all students
    cursor.execute("SELECT student_id, name, dob, age FROM students")
    students = cursor.fetchall()
    
    birthday_students = []
    
    for student_id, name, dob, age in students:
        # We expect dob format to be DD-MM-YYYY
        try:
            dob_day_month = dob[:5] # Extracts 'DD-MM'
            birth_year = int(dob[6:]) # Extracts 'YYYY'
            
            # If today is their birthday!
            if dob_day_month == current_day_month:
                birthday_students.append(name)
                
                # Calculate exactly how old they are turning today
                calculated_age = current_year - birth_year
                
                # Automatically update their age in the database if it's outdated
                if calculated_age != age:
                    cursor.execute("UPDATE students SET age = ? WHERE student_id = ?", (calculated_age, student_id))
                    
        except Exception as e:
            # Skips anyone whose DOB was typed incorrectly during registration
            pass 
            
    conn.commit()
    conn.close()
    
    return birthday_students