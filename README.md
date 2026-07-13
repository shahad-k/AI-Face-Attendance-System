# 🧠 AI Attendance Pro

> A professional, production-ready Windows Desktop Application for facial recognition-based attendance tracking and user database management.

AI Attendance Pro replaces outdated, manual attendance logging with an automated, high-precision Computer Vision engine. The system launches a secure Flask local web service and wraps it in a modern, single-process Desktop Control Panel, enabling seamless local network and offline operations.

---

## ✨ Features

- **🎯 Deep Learning Facial Recognition:** Real-time face detection and matching using `face_recognition` and `dlib` ResNet neural network models with sub-second response times.
- **😊 Smile Verification Check:** Integrated OpenCV Haar Cascade classifier requires users to smile during scanning to verify engagement and live attendance check.
- **🔒 Hashed Passcode Security:** Replaces legacy plain-text validations with secure `bcrypt` salt-hashing to protect administrative and user access.
- **🖥️ Launcher Control Panel:** Sleek dark-themed GUI launcher window featuring live status indicators, browser launching control, and secure daemon process management.
- **🎂 Interactive Birthday Module:** Automatically celebrates student birthdays with screen balloon animations and celebratory banners during attendance log-ins.
- **📊 Admin Portal:** Full interface for managing classes, viewing daily attendance sheets, manual student creation, and CSV exports.

---

## 🛠️ Tech Stack

- **Backend Logic:** Python 3.12, Flask
- **Frontend UI:** HTML5, CSS3, Vanilla JavaScript
- **Computer Vision:** OpenCV (v4.10.0 stable)
- **AI Models:** `dlib` & `face_recognition` (ResNet-based face embeddings)
- **Encryption:** `bcrypt` (Salted hashing)
- **Database:** SQLite3
- **App Packaging:** PyInstaller & Inno Setup

---

## 💾 Setup & Installation Guide

> **Note:** The compiled `dist/` executable and `.venv/` folders are hidden and ignored by GitHub Desktop (via `.gitignore`) to keep the codebase small and clean. Follow the instructions below to run or compile the project on your machine.

---

### 🚀 How to Open and Run via Command Prompt (CMD)
*Runs the project directly from the source code using Python.*

1. Open **Command Prompt (CMD)** and navigate to the project folder (for downloaded ZIPs, the folder name ends in `-main`):
   ```bash
   cd AI-Face-Attendance-System-main
   ```
   *(If you downloaded the ZIP, you may need to run `cd AI-Face-Attendance-System-main` twice to enter the inner folder).*

2. Create the virtual environment folder:
   ```bash
   python -m venv .venv
   ```
   *(Wait 10-15 seconds for the command to finish).*

3. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
   *(You will see `(.venv)` appear at the beginning of your terminal line).*

4. Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the application server:
   ```bash
   python run.py
   ```

---

### 📦 How to Build/Compile as a Standalone App (.exe)
*Converts the project into a double-clickable desktop application.*

> **Pre-requisite:** Ensure you have completed the **Setup Guide** above first to create your `.venv` environment and install all dependency packages!

1. Open **Command Prompt (CMD)** inside the project folder.

2. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```

3. Compile the application using the spec configuration:
   ```bash
   pyinstaller AIAttendanceSystem.spec --noconfirm
   ```

4. Automatically generate the Desktop Shortcut pointing to your new app:
   ```bash
   powershell -Command "$s = (New-Object -ComObject WScript.Shell).CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'AI Attendance Pro.lnk')); $s.TargetPath = '%CD%\dist\AIAttendanceSystem.exe'; $s.IconLocation = '%CD%\static\favicon.ico'; $s.Save()"
   ```
   *(A shortcut named **"AI Attendance Pro"** has been automatically created on your Desktop!)*

---

---

## 🔑 Admin Panel Access

Manage classes, view analytics sheets, register faces, and configure credentials using these default credentials:

- **Portal URL:** `http://127.0.0.1:5000/admin` (or click **Admin Portal** link on the home login screen)
- **Default Username:** `admin`
- **Default Password:** `admin`

*(We recommend changing the default passcode immediately inside the Admin Settings panel).*

---

## 🛠️ Troubleshooting & Runtimes

- **Application crashes immediately on startup:**
  *   *Cause:* The host PC lacks standard Microsoft C++ runtimes.
  *   *Solution:* Download and install the free **[Microsoft Visual C++ Redistributable Runtime (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)**.
- **Port Conflicts ("Server Failed to Start"):**
  *   *Cause:* Another background process is currently running on port 5000.
  *   *Solution:* The launcher is configured to automatically kill ghost processes on port 5000. If conflicts persist, check the Windows Task Manager and close any duplicate `python.exe` processes.
- **Windows SmartScreen Blue Warning:**
  *   *Cause:* Windows flags unsigned executable binaries downloaded from the internet.
  *   *Solution:* Click **"More Info"** and then **"Run anyway"**. To remove this permanently, the binary must be signed using a commercial digital certificate.

---

## 📝 Notes
- Biometric and face photograph data is processed and stored **100% locally** (no face profiles or images leave your machine).
- The database, dataset capture photos, and face encodings are saved in the same folder as the executable for persistent storage.
