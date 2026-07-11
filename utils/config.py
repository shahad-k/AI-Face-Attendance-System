# ==========================================
# SYSTEM CONFIGURATION FILE
# Change these values to update the whole app!
# ==========================================

# --- DATABASE SETTINGS ---
DB_PATH = "database/attendance_system.db"
DATASET_PATH = "dataset"
ENCODINGS_FILE = "encodings.pickle"

# --- SECURITY & PASSWORDS ---
# The master password required to register a new student
ADMIN_PASSWORD = "admin" 

# The unique PINs for each class teacher to start a session
TEACHER_PINS = {
    "10-A": "1001",
    "10-B": "1002",
    "11-Science": "2050",
    "11-Commerce": "2060",
    "12-Science": "3099",
    "12-Arts": "4011"
}

# --- UI COLORS (Dark Theme) ---
COLOR_SUCCESS = "#4CAF50" # Green
COLOR_ERROR = "#FF5252"   # Red
COLOR_WARNING = "#FFD700" # Yellow/Gold
COLOR_FEMALE = "#FFB6C1"  # Soft Pink
COLOR_MALE = "#FFD700"    # Gold