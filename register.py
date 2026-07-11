import cv2
import os
import sqlite3
import time
import face_recognition

# --- IMPORT CONFIG ---
from utils import config

def get_menu_choice(title, options, current_val=None):
    """Helper function to create a terminal dropdown/menu"""
    while True:
        print(f"\n{title}")
        if current_val:
            print(f"Current: [{current_val}] (Press ENTER to keep current)")
            
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")
            
        choice = input(f"Select an option (1-{len(options)}): ").strip()
        
        if current_val and choice == "":
            return current_val
            
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
            
        print("❌ Invalid selection. Please enter a valid number.")

def register_student():
    print("\n--- 🔒 SECURE REGISTRATION PORTAL ---")
    
    # --- USE CONFIG ADMIN PASSWORD ---
    password = input("Enter Principal/Mentor Password to unlock: ")
    if password != config.ADMIN_PASSWORD:
        print("❌ Incorrect Password. Access Denied!")
        return

    print("\n✅ Access Granted.")
    student_id = input("Enter Student ID: ").strip()

    # --- USE CONFIG DB PATH ---
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, roll_no, class, age, dob, gender FROM students WHERE student_id = ?", (student_id,))
    existing_student = cursor.fetchone()

    # Dynamically grab the classes from the config file!
    available_classes = list(config.TEACHER_PINS.keys())
    available_genders = ["MALE", "FEMALE"]

    if existing_student:
        print(f"\n⚠️ A student with ID '{student_id}' already exists!")
        print(f"Current Details -> Name: {existing_student[0]} | Roll No: {existing_student[1]}")
        
        edit_choice = input("\nDo you want to edit their details and retake photos? (y/n): ").strip().lower()
        if edit_choice != 'y':
            print("Registration cancelled.")
            conn.close()
            return
            
        print("\n✏️ Enter new details (or just press ENTER to keep the current value):")
        name = input(f"Full Name [{existing_student[0]}]: ").strip() or existing_student[0]
        roll_no = input(f"Roll No [{existing_student[1]}]: ").strip() or existing_student[1]
        
        student_class = get_menu_choice("Select Class:", available_classes, existing_student[2])
        age = input(f"Age [{existing_student[3]}]: ").strip() or str(existing_student[3])
        dob = input(f"Date of Birth [{existing_student[4]}]: ").strip() or existing_student[4]
        gender = get_menu_choice("Select Gender:", available_genders, existing_student[5])

        try:
            cursor.execute('''
                UPDATE students
                SET name = ?, roll_no = ?, class = ?, age = ?, dob = ?, gender = ?
                WHERE student_id = ?
            ''', (name, roll_no, student_class, age, dob, gender, student_id))
            conn.commit()
            print(f"\n✅ {name}'s details successfully updated!")
        except sqlite3.IntegrityError:
            print("\n❌ Error: The new Roll No you entered is already taken!")
            conn.close()
            return

    else:
        print("\n📝 New Student Detected. Enter Details:")
        name = input("Full Name: ").strip()
        roll_no = input("Roll No: ").strip()
        
        student_class = get_menu_choice("Select Class:", available_classes)
        age = input("Age: ").strip()
        dob = input("Date of Birth (DD-MM-YYYY): ").strip()
        gender = get_menu_choice("Select Gender:", available_genders)

        try:
            cursor.execute('''
                INSERT INTO students (student_id, name, roll_no, class, age, dob, gender)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, name, roll_no, student_class, age, dob, gender))
            conn.commit()
            print(f"\n✅ {name}'s details saved to the database!")
        except sqlite3.IntegrityError:
            print("\n❌ Error: A student with this Roll No already exists!")
            conn.close()
            return

    conn.close()

    # --- USE CONFIG DATASET PATH ---
    dataset_path = config.DATASET_PATH
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    print("\n📸 --- SMART PHOTO CAPTURE ---")
    print("Follow the on-screen instructions.")
    
    cam = cv2.VideoCapture(0)
    directions = ["Straight", "Slightly Left", "Slightly Right", "Slightly Up", "Slightly Down"]
    photos_taken = 0
    capture_timer = time.time()

    while photos_taken < 5:
        ret, frame = cam.read()
        if not ret:
            print("❌ Camera error.")
            break
            
        frame = cv2.flip(frame, 1)
        clean_frame = frame.copy()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_frame)
        current_direction = directions[photos_taken]

        if face_locations:
            top, right, bottom, left = face_locations[0]
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2
            radius = max(right - left, bottom - top) // 2
            
            cv2.circle(frame, (center_x, center_y), radius + 20, (0, 255, 0), 2)
            cv2.putText(frame, f"Look: {current_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            time_elapsed = time.time() - capture_timer
            countdown = max(0, 3 - int(time_elapsed))
            
            cv2.putText(frame, f"Auto-Capturing in: {countdown}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            if time_elapsed > 3:
                file_name = f"{roll_no}_{photos_taken + 1}.jpg"
                file_path = os.path.join(dataset_path, file_name)
                
                cv2.imwrite(file_path, clean_frame)
                print(f"📸 Automatically Captured {current_direction}!")
                
                photos_taken += 1
                capture_timer = time.time() 
        else:
            cv2.putText(frame, "❌ No face detected! Look at camera.", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            capture_timer = time.time() 

        cv2.imshow("Smart Registration", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            print("Registration cancelled.")
            break

    cam.release()
    cv2.destroyAllWindows()
    
    if photos_taken == 5:
        print(f"\n🎉 Smart Registration Complete! 5 perfect angles saved for {name}.")

if __name__ == "__main__":
    register_student()