@echo off
echo =========================================
echo    🚀 Starting AI Attendance System
echo =========================================

:: Start the Flask app in a separate background thread
start /B python app.py

echo.
echo ✅ Flask Server is running in the background.
echo ⏳ Starting Ngrok public tunnel...
echo.
echo =========================================
echo DO NOT CLOSE THIS WINDOW.
echo Ngrok will provide your public link below.
echo =========================================
echo.

:: Start ngrok with permanent domain
ngrok http --domain=backache-remission-possum.ngrok-free.dev 5000
