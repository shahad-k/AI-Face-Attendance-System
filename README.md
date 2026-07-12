# 🧠 AI-Powered Face Attendance & Management System

> An intelligent, automated Attendance Management System that leverages **Computer Vision** and **Machine Learning** to streamline classroom and office management.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🚀 Project Overview

Designed to replace manual, error-prone attendance taking, this system provides **real-time face verification** and a suite of engagement features — all running locally on your machine with zero cloud dependency.

### ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 **Facial Recognition Attendance** | Uses `face_recognition` and OpenCV to identify students and mark attendance with sub-second latency. |
| 📊 **Admin Dashboard** | A secure, GUI-based interface built with CustomTkinter for viewing records, filtering by class, and exporting logs to CSV. |
| 😊 **Smile Detection Engine** | Haar Cascade-based smile detection ensures students are present and engaged during check-in. |
| 🎂 **Birthday Celebration Module** | Detects a student's date of birth and launches an animated, interactive UI celebration with GIF cake effects. |
| 🔒 **Secure Multi-Room Gatekeeping** | Configurable PIN-based sessions restrict access to specific classrooms, ensuring data integrity. |
| ⚡ **Self-Healing Bootstrap** | `boot.py` automatically verifies dependencies, initializes the database, and launches the system. |

---

## 🛠 Technical Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.x |
| **Computer Vision** | OpenCV (Haar Cascades, VideoCapture) |
| **AI / ML** | `face_recognition`, `dlib` |
| **GUI Framework** | CustomTkinter (Dark Mode), Tkinter |
| **Database** | SQLite3 (Persistent storage with transactional integrity) |
| **Data Analysis** | pandas, matplotlib |

---

## 🚀 Quick Start — The "Antigravity" Installation

To eliminate **"dependency hell"**, this project includes a self-healing bootstrap system.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/attendance-ai.git
cd attendance-ai
```

### 2. Launch the System

```bash
python boot.py
```

**That's it!** `boot.py` will:

1. ✅ Verify installation of `opencv-python`, `customtkinter`, `face-recognition`, `pillow`, `pandas`, and `matplotlib`
2. 📦 Automatically `pip install` any missing packages
3. 🗃️ Initialize the SQLite database with the correct schema
4. 📂 Create required directories (`dataset/`, `encodings/`)
5. 🚀 Launch the `login.py` interface

---

## 📂 Project Structure

```
attendance-ai/
│
├── boot.py              # 🚀 Self-healing bootstrapper (start here!)
├── login.py             # 🔐 Secure portal — class selection + PIN auth
├── main.py              # 🎯 Core engine — camera feed + face recognition
├── register.py          # 📝 Student enrollment with guided photo capture
├── attendance.py        # 📊 Data viewer — filter & export attendance logs
├── admin.py             # 🏫 Admin dashboard — pie charts, tables, reports
├── birthday_ui.py       # 🎂 Animated birthday celebration popup
├── encode.py            # 🧬 Facial encoding generator (dataset → pickle)
├── setup_db.py          # 🗃️ Database schema initializer
│
├── utils/
│   ├── config.py        # ⚙️ Centralized configuration (PINs, paths, colors)
│   └── helpers.py       # 🔧 Birthday checking & age auto-update logic
│
├── assets/              # 🎨 Birthday cake GIF animations (8 variants)
├── database/            # 💾 SQLite database (auto-created)
├── dataset/             # 📸 Student face images (auto-created)
└── encodings/           # 🧬 Serialized face encoding files
```

---

## 🔧 How It Works

### 1. Registration Flow
```
register.py → Camera captures 5 angles → Saves to dataset/ → encode.py generates encodings.pickle
```

### 2. Attendance Flow
```
login.py (PIN auth) → main.py (live camera) → Face match → Smile check → DB insert → Dashboard update
```

### 3. Birthday Flow
```
Student recognized → DOB matches today → Animated GIF popup with countdown → "Wish Granted!" ✨
```

---

## ⚙️ Configuration

All settings are centralized in [`utils/config.py`](utils/config.py):

```python
# Database & file paths
DB_PATH = "database/attendance_system.db"
DATASET_PATH = "dataset"
ENCODINGS_FILE = "encodings.pickle"

# Security
ADMIN_PASSWORD = "admin"

# Teacher PINs (add/remove classes here)
TEACHER_PINS = {
    "10-A": "1001",
    "10-B": "1002",
    "11-Science": "2050",
    "11-Commerce": "2060",
    "12-Science": "3099",
    "12-Arts": "4011",
}
```

> **Tip:** Adding a new class is as simple as adding a new entry to `TEACHER_PINS`. The login dropdown, attendance filter, and registration form all update automatically.

---

## 🛡 Privacy & Security

This project prioritizes user privacy:

- **🔐 Data Handling:** Facial encodings are stored as mathematical vectors (`.pickle` format), not raw images
- **💻 Local Processing:** All video data is processed locally — no biometric data leaves your machine
- **🔑 PIN Protection:** Each class session requires a unique teacher PIN
- **🔒 Admin Gate:** Student registration requires the admin/principal password

---

## 📝 Roadmap

- [ ] SMS/Email API integration to notify parents of attendance
- [ ] Cloud-sync capabilities for multi-campus deployment
- [ ] Enhanced anti-spoofing (liveness detection) to prevent photo-based attacks
- [ ] Excel export support alongside CSV
- [ ] Full student database management in admin panel

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Released under the **MIT License**. Feel free to use, modify, and distribute this software for educational or commercial purposes.
