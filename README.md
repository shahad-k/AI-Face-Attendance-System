# 🧠 AI-Powered Face Attendance & Management System

> An intelligent, automated Attendance Management System that leverages **Computer Vision** and **Machine Learning** to streamline classroom and office management.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🚀 Project Overview

Designed to replace manual, error-prone attendance taking, this system provides **real-time face verification** and a suite of engagement features. **Recently upgraded to a full Flask Web Application**, the system can now be accessed via any web browser on your local network or over the public internet!

### ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 **Facial Recognition Attendance** | Uses `face_recognition` and OpenCV to identify students and mark attendance with sub-second latency. |
| 🌐 **Modern Web Interface** | Clean, responsive web dashboard built with HTML, CSS, and JS (replacing the old Tkinter GUI). |
| 📊 **Admin Dashboard** | Secure portal for viewing records, filtering by class, managing student databases, and exporting logs. |
| 😊 **Smile Detection Engine** | Haar Cascade-based smile detection ensures students are present and engaged during check-in. |
| 🎂 **Birthday Celebration Module** | Detects a student's date of birth and launches an animated birthday banner and celebration popup. |
| 🔒 **Secure Role-based Access** | PIN-based sessions for teachers (`/camera`) and secure password protection for Admins (`/admin`). |

---

## 🛠 Technical Stack

| Component | Technology |
|---|---|
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Computer Vision** | OpenCV (Haar Cascades, VideoCapture) |
| **AI / ML** | `face_recognition`, `dlib` |
| **Database** | SQLite3 (Persistent storage with transactional integrity) |

---

## 🚀 Installation & Usage

## 🚀 Installation & Usage

Follow these **3 extremely simple steps** to safely run the AI system on your computer.

### Step 1: Download the Project
The safest and best way to download this project is using Git. (Downloading via ZIP can trigger Windows security warnings, which we explain below).
Open your terminal and paste this command:
```bash
git clone https://github.com/yourusername/attendance-ai.git
```
*If you downloaded the ZIP file instead, extract the folder to your computer.*

### Step 2: Create Environment & Install Dependencies
1. Open the `attendance-ai` folder you just downloaded.
2. **Windows Trick:** Click the folder's address bar at the very top, delete the text, type `cmd`, and hit **Enter**. This instantly opens a black terminal window in the right place!
3. Paste this command to create a virtual environment and install all dependencies (including PyInstaller and security packages) at once:
```bash
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
```

### Step 3: Launch the System!
To start the AI server safely without any scary Windows security warnings, just paste this command into your terminal:
```bash
python run.py
```
🎉 **That's it!** The system will check your dependencies, boot up the server, and automatically pop open your web browser to the dashboard!

---

## 🛡️ Why NO `.bat` files? (Windows SmartScreen Explained)
You might notice there are no `.bat` or `.exe` files in this project to double-click. **This is for your safety.**
Whenever you download a ZIP file from the internet, Windows activates a security feature called **SmartScreen ("Mark of the Web")**. It aggressively blocks downloaded `.bat` files with a scary blue warning: *"Windows protected your PC / This file may be dangerous"*.

To ensure everyone feels **100% safe** running this open-source project, we use a standard Python script (`run.py`). Running it via the terminal completely avoids false-alarm security blocks and ensures a clean, professional setup.

*Note: On your very first run, the system will automatically create the SQLite database and necessary folders for you.*

---

## 🌍 How to Make the App Public (Using Ngrok)

If you want to access the attendance camera from a tablet in the classroom or share it securely over the internet, you must use **HTTPS** (browsers block webcams on standard HTTP). Ngrok is the easiest way to do this for free!

1. Go to [ngrok.com](https://ngrok.com/) and create a free account.
2. Download the Ngrok app for Windows/Mac and authenticate it.
3. Keep your Flask app running (`python app.py`).
4. Open a **new** terminal window and run:
   ```bash
   ngrok http 5000
   ```
5. Ngrok will give you a secure, public HTTPS link (e.g., `https://a1b2c3d4.ngrok-free.app`). 
6. Open that link on any device in the world to access your AI Server!

---

## 📂 Project Structure

```text
attendance-ai/
│
├── app.py               # 🚀 Main Flask Backend Engine (start here!)
├── templates/           # 🌐 HTML Pages
│   ├── login.html       # Teacher PIN portal
│   ├── dashboard.html   # Live stats & class selection
│   ├── camera.html      # AI Face Recognition interface
│   ├── register.html    # Guided new student registration
│   └── admin.html       # Full admin control panel
│
├── static/              
│   └── style.css        # 🎨 Unified CSS Styling
│
├── database/            # 💾 SQLite database (auto-created)
├── dataset/             # 📸 Student face images (auto-created)
└── encodings.pickle     # 🧬 Serialized face encoding vectors
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

## 📦 Standalone Windows Executable (.exe)

This application can be compiled into a single, standalone Windows `.exe` that runs on any PC without requiring Python, Git, or manual package installations!

### Default Admin Credentials
- **Access URL:** `/admin` (or click "Admin Portal" from the home page)
- **Master Admin Password:** `admin` (You can change this password securely inside the admin panel under Settings).

---

### 🔨 How to Build the Executable

Follow these steps to compile the project into a standalone executable:

1. **Activate the Virtual Environment:**
   ```bash
   .venv\Scripts\activate
   ```
2. **Compile the App using the Spec File:**
   ```bash
   .venv\Scripts\pyinstaller AIAttendanceSystem.spec --noconfirm
   ```
   *This compiles the application using the custom configurations inside `AIAttendanceSystem.spec` (hiding the console window, bundling templates, static files, and `face_recognition` shape models).*
3. **Get your Executable:**
   Once compilation is complete, find your standalone executable `AIAttendanceSystem.exe` inside the `dist/` directory!

---

### 💻 How to Run & Test on Another PC

1. Copy the `AIAttendanceSystem.exe` from the `dist/` directory to the target Windows PC (e.g. via USB flash drive).
2. Double-click the `.exe` to launch it.
3. A sleek slate-themed **Control Panel** window will open in the background, and your default web browser will automatically load the local attendance portal at `http://127.0.0.1:5000/`.
4. When finished, simply click **"Shutdown Server"** in the Control Panel window to close the background server cleanly.

---

### 🛠️ Troubleshooting & Known Errors

If you encounter installation issues (especially during clean manual setups), check these solutions:

#### 1. `ERROR: Failed building wheel for dlib`
**Why it happens:** Installing `dlib` from scratch on Windows requires C++ compilers (like CMake and Visual C++ Build Tools).
**The Fix:** Use a precompiled dlib binary wheel for Python 3.10 instead of building it from source:
```bash
pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.22.99-cp310-cp310-win_amd64.whl
```

#### 2. `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE`
**Why it happens:** Cached package files on your PC have corrupted or modified checksum hashes.
**The Fix:** Clear your pip download cache and force a clean reinstall:
```bash
pip install --no-cache-dir -r requirements.txt
```

#### 3. Executable immediately crashes on start on another PC
**Why it happens:** Some Windows PCs lack runtime Visual C++ Redistributable packages.
**The Fix:** Install the standard [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) package on the target PC (which contains the required C++ runtimes for `dlib` and `opencv`).

---

## 📄 License

Released under the **MIT License**. Feel free to use, modify, and distribute this software for educational or commercial purposes.

