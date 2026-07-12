"""
AI-Powered Face Attendance & Management System — Flask Web Application
=====================================================================
Full web version with live camera face recognition, auto attendance,
smile detection, registration, birthday celebration, and admin panel.
"""

import sys
import io as _io

# --- Fix Windows console encoding for emoji/unicode ---
if sys.stdout.encoding != 'utf-8':
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, Response
)
import sqlite3
import os
import csv
import io
import base64
import pickle
import threading
from datetime import datetime
from functools import wraps

# --- IMPORT PROJECT CONFIG ---
from utils import config
from utils.helpers import check_and_update_birthdays

# --- Optional CV/AI imports (graceful if missing) ---
try:
    import cv2
    import numpy as np
    import face_recognition
    CV_AVAILABLE = True
except (ImportError, SystemExit, Exception):
    CV_AVAILABLE = False

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "attendance-ai-flask-secret-key-2024"

# --- FACE ENCODINGS CACHE ---
known_data = {"encodings": [], "roll_nos": []}
encodings_lock = threading.Lock()
marked_today = set()
wished_today = set()


def load_encodings():
    """Load face encodings from pickle file."""
    global known_data
    encodings_path = os.path.join(BASE_DIR, config.ENCODINGS_FILE)
    try:
        with open(encodings_path, "rb") as f:
            known_data = pickle.load(f)
        print(f"  Loaded {len(known_data['encodings'])} face encodings.")
    except FileNotFoundError:
        known_data = {"encodings": [], "roll_nos": []}
        print("  No encodings.pickle found. Register students first.")


# Load encodings at startup
if CV_AVAILABLE:
    load_encodings()
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')


# ============================================================
# DATABASE HELPER
# ============================================================
def get_db():
    """Returns a database connection with Row factory for dict-like access."""
    db_path = os.path.join(BASE_DIR, config.DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Ensure database and required tables exist."""
    db_folder = os.path.join(BASE_DIR, "database")
    os.makedirs(db_folder, exist_ok=True)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Students & Attendance
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        roll_no TEXT NOT NULL UNIQUE,
        class TEXT NOT NULL,
        age INTEGER,
        dob TEXT,
        gender TEXT DEFAULT 'MALE'
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        smiled TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (student_id)
    )''')
    
    # Classes Management
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS classes (
        class_name TEXT PRIMARY KEY,
        passcode TEXT NOT NULL UNIQUE,
        mentor_name TEXT DEFAULT ''
    )''')
    
    # Ensure classes table has passcode instead of pin (migration)
    try:
        cursor.execute("ALTER TABLE classes RENAME COLUMN pin TO passcode")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    # Settings Management
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    # Birthday Wishes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS birthday_wishes (
        student_id TEXT PRIMARY KEY,
        date TEXT NOT NULL
    )''')
    
    # Migrate initial data from config.py if tables are empty
    cursor.execute("SELECT COUNT(*) as cnt FROM classes")
    if cursor.fetchone()["cnt"] == 0:
        for cls, pin in config.TEACHER_PINS.items():
            cursor.execute("INSERT INTO classes (class_name, passcode, mentor_name) VALUES (?, ?, ?)", (cls, pin, ""))
            
    cursor.execute("SELECT COUNT(*) as cnt FROM settings")
    if cursor.fetchone()["cnt"] == 0:
        cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("admin_password", config.ADMIN_PASSWORD))
        
    conn.commit()
    conn.close()


# ============================================================
# AUTH DECORATORS
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow admins to access teacher APIs (fixes infinite loading bug in admin panel)
        if "logged_in" not in session and not session.get("admin"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login_page"))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# PAGE ROUTES
# ============================================================
@app.route("/")
def login_page():
    if "logged_in" in session:
        return redirect(url_for("camera_page"))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT class_name FROM classes ORDER BY class_name")
    classes = [r["class_name"] for r in cursor.fetchall()]
    conn.close()
    return render_template("login.html", classes=classes)


@app.route("/login", methods=["POST"])
def do_login():
    selected_class = request.form.get("class_name") or request.form.get("class")
    entered_pin = request.form.get("pin")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT passcode FROM classes WHERE class_name = ?", (selected_class,))
    row = cursor.fetchone()
    conn.close()
    
    db_passcode = row["passcode"] if row else None
    
    # Temporary Debug Safety Check
    print(f"[DEBUG LOGIN] Selected Class: {selected_class}")
    print(f"[DEBUG LOGIN] Entered PIN: '{entered_pin}' (type: {type(entered_pin)})")
    print(f"[DEBUG LOGIN] Database Passcode: '{db_passcode}' (type: {type(db_passcode)})")
    
    if db_passcode is not None and str(entered_pin).strip() == str(db_passcode).strip():
        session["logged_in"] = True
        session["current_class"] = selected_class
        print("[DEBUG LOGIN] Validation Successful")
        return redirect(url_for("camera_page"))
    else:
        print("[DEBUG LOGIN] Validation Failed")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT class_name FROM classes ORDER BY class_name")
        classes = [r["class_name"] for r in cursor.fetchall()]
        conn.close()
        return render_template("login.html", classes=classes, error="Invalid PIN for this class.")


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT class_name FROM classes ORDER BY class_name")
    classes = ["All Classes"] + [r["class_name"] for r in cursor.fetchall()]
    conn.close()
    current_class = session.get("current_class", "All Classes")
    return render_template("dashboard.html", classes=classes, current_class=current_class)


@app.route("/camera")
@login_required
def camera_page():
    """Live camera page for AI face recognition attendance."""
    current_class = session.get("current_class", "All Classes")
    mentor_name = ""
    if current_class != "All Classes":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT mentor_name FROM classes WHERE class_name = ?", (current_class,))
        row = cursor.fetchone()
        conn.close()
        if row:
            mentor_name = row["mentor_name"]
    return render_template("camera.html", current_class=current_class, mentor_name=mentor_name, cv_available=CV_AVAILABLE)


@app.route("/register")
@login_required
def register_page():
    """Student registration page with webcam photo capture."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT class_name FROM classes ORDER BY class_name")
    classes = [r["class_name"] for r in cursor.fetchall()]
    conn.close()
    return render_template("register.html", classes=classes)


@app.route("/admin")
def admin_login_page():
    return render_template("admin_login.html")


@app.route("/admin/login", methods=["POST"])
def admin_do_login():
    password = request.form.get("password")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_password'")
    row = cursor.fetchone()
    conn.close()
    
    correct_password = row["value"] if row else config.ADMIN_PASSWORD
    
    if password == correct_password:
        session["admin"] = True
        return redirect(url_for("admin_panel"))
    return render_template("admin_login.html", error="Incorrect Password!")


@app.route("/admin/panel")
@admin_required
def admin_panel():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT class_name FROM classes ORDER BY class_name")
    classes = ["All Classes"] + [r["class_name"] for r in cursor.fetchall()]
    conn.close()
    return render_template("admin.html", classes=classes)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ============================================================
# JSON API ROUTES
# ============================================================
@app.route("/api/attendance")
@login_required
def api_attendance():
    selected_class = request.args.get("class", "All Classes")
    today_str = datetime.now().strftime("%d-%m-%Y")
    conn = get_db()
    cursor = conn.cursor()
    if selected_class == "All Classes":
        cursor.execute("""
            SELECT s.student_id, s.name, s.roll_no, s.class, a.time, a.smiled
            FROM attendance a JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ? ORDER BY a.time DESC
        """, (today_str,))
    else:
        cursor.execute("""
            SELECT s.student_id, s.name, s.roll_no, s.class, a.time, a.smiled
            FROM attendance a JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ? AND s.class = ? ORDER BY a.time DESC
        """, (today_str, selected_class))
    records = cursor.fetchall()
    conn.close()
    return jsonify([{"student_id": r["student_id"], "name": r["name"], "roll_no": r["roll_no"],
                     "class": r["class"], "time": r["time"], "smiled": r["smiled"]} for r in records])


@app.route("/api/stats")
@login_required
def api_stats():
    today_str = datetime.now().strftime("%d-%m-%Y")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM students")
    total = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(DISTINCT a.student_id) as cnt FROM attendance a WHERE a.date = ?", (today_str,))
    present = cursor.fetchone()["cnt"]
    conn.close()
    return jsonify({"total": total, "present": present, "absent": total - present, "date": today_str})


@app.route("/api/birthdays")
@login_required
def api_birthdays():
    # Update student ages in DB if today is their birthday
    check_and_update_birthdays()
    
    # Only return names of students whose birthday is today AND who checked in today
    today_str = datetime.now().strftime("%d-%m-%Y")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name 
        FROM birthday_wishes bw 
        JOIN students s ON bw.student_id = s.student_id 
        WHERE bw.date = ?
    """, (today_str,))
    names = [row["name"] for row in cursor.fetchall()]
    conn.close()
    return jsonify(names)


@app.route("/api/students")
@admin_required
def api_students():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, roll_no, class, age, dob, gender FROM students ORDER BY class, roll_no")
    students = cursor.fetchall()
    conn.close()
    return jsonify([{"student_id": s["student_id"], "name": s["name"], "roll_no": s["roll_no"],
                     "class": s["class"], "age": s["age"], "dob": s["dob"], "gender": s["gender"]} for s in students])


@app.route("/api/student/<roll_no>/delete", methods=["POST"])
@admin_required
def api_delete_student(roll_no):
    """Deletes a student from the DB and removes their dataset photos."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Delete from DB
        cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
        conn.commit()

        # Delete from dataset folder
        dataset_path = os.path.join(BASE_DIR, config.DATASET_PATH)
        if os.path.exists(dataset_path):
            for file_name in os.listdir(dataset_path):
                if file_name.startswith(f"{roll_no}_"):
                    os.remove(os.path.join(dataset_path, file_name))
        
        # We don't automatically regenerate encodings here for speed,
        # but the admin can click "Generate Encodings" in the UI later or 
        # the system will just ignore unknown faces. 
        # Actually, let's regenerate it in the background if CV is available
        if CV_AVAILABLE:
            threading.Thread(target=regenerate_encodings_bg).start()

        return jsonify({"status": "ok", "message": f"Student {roll_no} deleted."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()


@app.route("/api/classes", methods=["GET", "POST"])
@admin_required
def api_classes():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("SELECT class_name, passcode, mentor_name FROM classes ORDER BY class_name")
        classes = [{"class_name": r["class_name"], "passcode": r["passcode"], "pin": r["passcode"], "mentor_name": r["mentor_name"]} for r in cursor.fetchall()]
        conn.close()
        return jsonify(classes)
    elif request.method == "POST":
        data = request.json
        original_name = data.get("original_name")
        class_name = data.get("class_name")
        passcode = data.get("passcode") or data.get("pin")
        mentor_name = data.get("mentor_name", "")
        
        try:
            if original_name:
                cursor.execute("UPDATE classes SET class_name=?, passcode=?, mentor_name=? WHERE class_name=?", 
                               (class_name, passcode, mentor_name, original_name))
            else:
                cursor.execute("INSERT INTO classes (class_name, passcode, mentor_name) VALUES (?, ?, ?)", 
                               (class_name, passcode, mentor_name))
            conn.commit()
            return jsonify({"status": "ok", "message": "Class saved successfully"})
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "Class name or Passcode already exists."})
        finally:
            conn.close()


@app.route("/api/classes/<class_name>", methods=["DELETE"])
@admin_required
def api_delete_class(class_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE class_name = ?", (class_name,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "message": "Class deleted successfully"})


@app.route("/api/student/check/<student_id>", methods=["GET"])
@login_required
def api_check_student(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, roll_no, class, age, dob, gender FROM students WHERE student_id = ?", (student_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            "exists": True,
            "student": {
                "student_id": row["student_id"],
                "name": row["name"],
                "roll_no": row["roll_no"],
                "class": row["class"],
                "age": row["age"],
                "dob": row["dob"],
                "gender": row["gender"]
            }
        })
    return jsonify({"exists": False})


@app.route("/api/students/manual", methods=["POST"])
@admin_required
def api_add_student_manual():
    data = request.json
    student_id = data.get("student_id", "").strip()
    name = data.get("name", "").strip()
    roll_no = data.get("roll_no", "").strip()
    class_name = data.get("class", "").strip()
    gender = data.get("gender", "MALE").strip()
    age = data.get("age")
    dob = data.get("dob", "").strip()
    
    if not student_id or not name or not roll_no or not class_name:
        return jsonify({"status": "error", "message": "Required fields are missing."})
        
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Check duplicate student_id
        cursor.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Student ID already exists."})
            
        # Check duplicate roll_no
        cursor.execute("SELECT 1 FROM students WHERE roll_no = ?", (roll_no,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Roll Number already exists."})
            
        cursor.execute("""
            INSERT INTO students (student_id, name, roll_no, class, age, dob, gender)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_id, name, roll_no, class_name, age, dob, gender))
        conn.commit()
        return jsonify({"status": "ok", "message": "Student added successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()


@app.route("/api/settings/password", methods=["POST"])
@admin_required
def api_change_password():
    data = request.json
    current_password = data.get("current_password")
    new_password = data.get("password")
    if not current_password or not new_password:
        return jsonify({"status": "error", "message": "All password fields are required"})
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_password'")
    row = cursor.fetchone()
    correct_password = row["value"] if row else config.ADMIN_PASSWORD
    if current_password != correct_password:
        conn.close()
        return jsonify({"status": "error", "message": "Incorrect current password"})
    cursor.execute("UPDATE settings SET value = ? WHERE key = 'admin_password'", (new_password,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "message": "Admin password updated successfully"})


def regenerate_encodings_bg():
    """Background task to regenerate encodings after deletion."""
    try:
        dataset_path = os.path.join(BASE_DIR, config.DATASET_PATH)
        encodings_path = os.path.join(BASE_DIR, config.ENCODINGS_FILE)
        new_encodings = []
        new_roll_nos = []
        for file_name in os.listdir(dataset_path):
            if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')): continue
            r_no = file_name.split("_")[0]
            try:
                image = cv2.imread(os.path.join(dataset_path, file_name))
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                encs = face_recognition.face_encodings(rgb)
                if encs:
                    new_encodings.append(encs[0])
                    new_roll_nos.append(r_no)
            except: pass
        with open(encodings_path, "wb") as f:
            pickle.dump({"encodings": new_encodings, "roll_nos": new_roll_nos}, f)
        with encodings_lock:
            load_encodings()
    except Exception as e:
        print("BG Encoding Error:", e)


# ============================================================
# FACE RECOGNITION API
# ============================================================
@app.route("/api/recognize", methods=["POST"])
@login_required
def api_recognize():
    """Receives a webcam frame (base64), runs face recognition, marks attendance."""
    if not CV_AVAILABLE:
        return jsonify({"status": "error", "message": "Face recognition libraries not installed."})

    data = request.json
    frame_b64 = data.get("frame", "")
    current_class = session.get("current_class", "All Classes")

    try:
        # Decode base64 image
        if "," in frame_b64:
            frame_b64 = frame_b64.split(",")[1]
        img_bytes = base64.b64decode(frame_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Invalid image data."})

        # Resize for speed (same as desktop app)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small)
        if not face_locations:
            return jsonify({"status": "no_face"})

        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
        if not face_encodings:
            return jsonify({"status": "no_face"})

        with encodings_lock:
            if not known_data["encodings"]:
                return jsonify({"status": "no_encodings", "message": "No students registered yet."})

            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_data["encodings"], face_encoding, tolerance=0.5)

                if True not in matches:
                    continue

                matched_idx = matches.index(True)
                roll_no = known_data["roll_nos"][matched_idx]

                # Look up student in DB
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT student_id, name, class, gender, age, dob FROM students WHERE roll_no = ?", (roll_no,))
                student = cursor.fetchone()

                if not student:
                    conn.close()
                    return jsonify({"status": "unknown", "message": f"Roll No '{roll_no}' not in database."})

                student_id = student["student_id"]
                name = student["name"]
                student_class = student["class"]
                gender = student["gender"]
                student_age = student["age"]
                dob = student["dob"]

                # CLASS GATEKEEPER
                if current_class != "All Classes" and student_class != current_class:
                    conn.close()
                    return jsonify({
                        "status": "wrong_class", "name": name, "class": student_class, "roll_no": roll_no,
                        "message": f"Wrong Room! This session is for {current_class}."
                    })

                # ALREADY MARKED (Database check)
                now = datetime.now()
                date_str = now.strftime("%d-%m-%Y")
                time_str = now.strftime("%H:%M:%S")
                
                cursor.execute("SELECT 1 FROM attendance WHERE student_id = ? AND date = ?", (student_id, date_str))
                if cursor.fetchone():
                    conn.close()
                    if gender == "FEMALE":
                        msg = "My lady... you already marked your presence."
                    else:
                        msg = "Bro, you already locked in your attendance. Go conquer the day!"
                    return jsonify({
                        "status": "already_marked", "name": name, "class": student_class,
                        "roll_no": roll_no, "gender": gender, "message": msg
                    })

                # SMILE DETECTION
                top4, right4, bottom4, left4 = top * 4, right * 4, bottom * 4, left * 4
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                top4, bottom4 = max(0, top4), min(gray.shape[0], bottom4)
                left4, right4 = max(0, left4), min(gray.shape[1], right4)
                face_roi = gray[top4:bottom4, left4:right4]
                is_smiling = "No"
                if face_roi.shape[0] > 0 and face_roi.shape[1] > 0:
                    smiles = smile_cascade.detectMultiScale(face_roi, scaleFactor=1.8, minNeighbors=20)
                    if len(smiles) > 0:
                        is_smiling = "Yes"

                # MARK ATTENDANCE
                cursor.execute("INSERT INTO attendance (student_id, date, time, smiled) VALUES (?, ?, ?, ?)",
                               (student_id, date_str, time_str, is_smiling))
                conn.commit()

                # BIRTHDAY CHECK (Saves birthday wishes dynamically)
                is_birthday = False
                if dob and len(dob) >= 5:
                    dob_day_month = dob[:5]
                    today_day_month = now.strftime("%d-%m")
                    if dob_day_month == today_day_month:
                        is_birthday = True
                        cursor.execute("INSERT OR REPLACE INTO birthday_wishes (student_id, date) VALUES (?, ?)", (student_id, date_str))
                        conn.commit()

                conn.close()
                return jsonify({
                    "status": "marked", "name": name, "class": student_class, "roll_no": roll_no,
                    "gender": gender, "age": student_age, "smiled": is_smiling,
                    "time": time_str, "is_birthday": is_birthday,
                    "message": "Attendance Marked Successfully!"
                })

        return jsonify({"status": "unknown", "message": "Face not recognized."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ============================================================
# REGISTRATION API
# ============================================================
@app.route("/api/register", methods=["POST"])
@login_required
def api_register():
    """Register a new student or update existing one."""
    data = request.json
    password = data.get("password", "")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_password'")
    row = cursor.fetchone()
    
    correct_password = row["value"] if row else config.ADMIN_PASSWORD
    if password != correct_password:
        conn.close()
        return jsonify({"status": "error", "message": "Incorrect Admin Master Password!"})
    

    student_id = data.get("student_id", "").strip()
    name = data.get("name", "").strip()
    roll_no = data.get("roll_no", "").strip()
    student_class = data.get("class", "").strip()
    age = data.get("age", "").strip()
    dob = data.get("dob", "").strip()
    gender = data.get("gender", "MALE").strip()

    if not all([student_id, name, roll_no, student_class]):
        return jsonify({"status": "error", "message": "Student ID, Name, Roll No, and Class are required."})

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE students SET name=?, roll_no=?, class=?, age=?, dob=?, gender=?
                WHERE student_id=?
            """, (name, roll_no, student_class, age, dob, gender, student_id))
            conn.commit()
            conn.close()
            return jsonify({"status": "updated", "message": f"{name}'s details updated!"})
        else:
            cursor.execute("""
                INSERT INTO students (student_id, name, roll_no, class, age, dob, gender)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, name, roll_no, student_class, age, dob, gender))
            conn.commit()
            conn.close()
            return jsonify({"status": "created", "message": f"{name} registered successfully!"})

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "error", "message": "A student with this Roll No already exists."})


@app.route("/api/save-photo", methods=["POST"])
@login_required
def api_save_photo():
    """Save a captured webcam photo for a student."""
    data = request.json
    roll_no = data.get("roll_no", "").strip()
    photo_index = data.get("index", 1)
    frame_b64 = data.get("frame", "")

    if not roll_no or not frame_b64:
        return jsonify({"status": "error", "message": "Missing data."})

    dataset_path = os.path.join(BASE_DIR, config.DATASET_PATH)
    os.makedirs(dataset_path, exist_ok=True)

    try:
        if "," in frame_b64:
            frame_b64 = frame_b64.split(",")[1]
        img_bytes = base64.b64decode(frame_b64)
        file_name = f"{roll_no}_{photo_index}.jpg"
        file_path = os.path.join(dataset_path, file_name)

        with open(file_path, "wb") as f:
            f.write(img_bytes)

        return jsonify({"status": "ok", "message": f"Photo {photo_index} saved.", "file": file_name})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/encode-faces", methods=["POST"])
@login_required
def api_encode_faces():
    """Re-generate encodings.pickle from all photos in the dataset folder."""
    if not CV_AVAILABLE:
        return jsonify({"status": "error", "message": "Face recognition libraries not installed."})

    dataset_path = os.path.join(BASE_DIR, config.DATASET_PATH)
    encodings_path = os.path.join(BASE_DIR, config.ENCODINGS_FILE)

    new_encodings = []
    new_roll_nos = []
    processed = 0
    failed = 0

    for file_name in os.listdir(dataset_path):
        if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        roll_no = file_name.split("_")[0]
        image_path = os.path.join(dataset_path, file_name)
        try:
            image = cv2.imread(image_path)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_image)
            if len(encodings) > 0:
                new_encodings.append(encodings[0])
                new_roll_nos.append(roll_no)
                processed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    data_to_save = {"encodings": new_encodings, "roll_nos": new_roll_nos}
    with open(encodings_path, "wb") as f:
        pickle.dump(data_to_save, f)

    with encodings_lock:
        load_encodings()

    return jsonify({
        "status": "ok",
        "message": f"Encoding complete! {processed} faces encoded, {failed} failed.",
        "processed": processed, "failed": failed
    })


# ============================================================
# CSV EXPORT
# ============================================================
@app.route("/export/csv")
@login_required
def export_csv():
    selected_class = request.args.get("class", "All Classes")
    today_str = datetime.now().strftime("%d-%m-%Y")
    conn = get_db()
    cursor = conn.cursor()
    if selected_class == "All Classes":
        cursor.execute("""
            SELECT s.student_id, s.name, s.roll_no, s.class, a.time, a.smiled
            FROM attendance a JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ? ORDER BY a.time DESC
        """, (today_str,))
    else:
        cursor.execute("""
            SELECT s.student_id, s.name, s.roll_no, s.class, a.time, a.smiled
            FROM attendance a JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ? AND s.class = ? ORDER BY a.time DESC
        """, (today_str, selected_class))
    records = cursor.fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Full Name", "Roll No", "Class", "Check-In Time", "Smiled?"])
    for r in records:
        writer.writerow([r["student_id"], r["name"], r["roll_no"], r["class"], r["time"], r["smiled"]])
    filename = f"Attendance_{selected_class}_{today_str}.csv"
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


# ============================================================
# LAUNCH
# ============================================================
if __name__ == "__main__":
    init_db()
    print("\n  AI Attendance System - Web Interface")
    print("  Open http://127.0.0.1:5000/ in your browser")
    if not CV_AVAILABLE:
        print("  [WARNING] face_recognition/opencv not found. Camera features disabled.")
    print()
    app.run(debug=True, use_reloader=False)