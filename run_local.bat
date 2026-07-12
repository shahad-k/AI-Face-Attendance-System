@echo off
echo =========================================
echo    🚀 Starting AI Attendance System
echo =========================================

echo.
echo [1] Starting Local AI Server...
start /B python app.py

echo [2] Waiting for server to initialize...
timeout /t 3 /nobreak > NUL

echo [3] Opening your Web Browser...
start http://127.0.0.1:5000

echo.
echo ✅ System is now running! 
echo Keep this black window open while using the system.
echo To stop the server, just close this window.
echo =========================================
pause
