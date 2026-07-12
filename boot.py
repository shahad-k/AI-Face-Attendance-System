import subprocess
import sys
import os
import sqlite3
import io

# --- Fix Windows console encoding for emoji/unicode ---
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# --- Ensure we are always running from the project directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# --- Map pip package names to their actual Python import names ---
DEPENDENCIES = {
    "opencv-python": "cv2",
    "customtkinter": "customtkinter",
    "face-recognition": "face_recognition",
    "pillow": "PIL",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
}

def install_dependencies():
    """Verifies and installs all required Python packages."""
    print("🚀 Checking system requirements...\n")

    all_good = True
    for pip_name, import_name in DEPENDENCIES.items():
        try:
            __import__(import_name)
            print(f"  ✅ {pip_name} is already installed.")
        except ImportError:
            all_good = False
            print(f"  📦 Installing {pip_name}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )
                print(f"  ✅ {pip_name} installed successfully.")
            except subprocess.CalledProcessError:
                print(f"  ❌ Failed to install {pip_name}. Please install it manually.")
                sys.exit(1)

    if all_good:
        print("\n  ✅ All packages already present.")

    # --- Install face_recognition_models (required by face_recognition) ---
    try:
        import face_recognition_models
        print("  ✅ face_recognition_models is already installed.")
    except ImportError:
        print("  📦 Installing face_recognition_models (required for face detection)...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install",
                 "git+https://github.com/ageitgey/face_recognition_models"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            print("  ✅ face_recognition_models installed successfully.")
        except subprocess.CalledProcessError:
            print("  ⚠️  Could not auto-install face_recognition_models.")
            print("     Run manually: pip install git+https://github.com/ageitgey/face_recognition_models")


def initialize_database():
    """Ensures the SQLite database exists with the correct schema."""
    print("\n🗃️  Verifying database...")

    db_folder = os.path.join(BASE_DIR, "database")
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        print("  📁 Created 'database' folder.")

    db_path = os.path.join(db_folder, "attendance_system.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        roll_no TEXT NOT NULL UNIQUE,
        class TEXT NOT NULL,
        age INTEGER,
        dob TEXT,
        gender TEXT DEFAULT 'MALE'
    )
    ''')

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

    # Ensure the gender column exists for databases created with the old schema
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN gender TEXT DEFAULT 'MALE'")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()
    print("  ✅ Database is ready.")


def ensure_directories():
    """Creates required directories if they don't exist."""
    print("\n📂 Checking project directories...")
    for folder in ["dataset", "encodings"]:
        path = os.path.join(BASE_DIR, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"  📁 Created '{folder}' folder.")
    print("  ✅ All directories present.")


def launch():
    """Launches the login interface."""
    print("\n🎉 All systems go! Launching Attendance AI...\n")
    print("=" * 50)
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "login.py")])


if __name__ == "__main__":
    print("=" * 50)
    print("   🧠 AI Attendance System — Antigravity Boot")
    print("=" * 50)
    install_dependencies()
    initialize_database()
    ensure_directories()
    launch()