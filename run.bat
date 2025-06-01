@echo off
echo ========================================
echo    Screen Translator - Real-time OCR
echo ========================================
echo.

REM ตรวจสอบว่ามี Python3 หรือไม่
python3 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python3 ไม่พบในระบบ
    echo กรุณาติดตั้ง Python 3.7+ จาก https://python.org
    echo หรือ alias python3 ใน PowerShell: Set-Alias python3 python
    pause
    exit /b 1
)

echo ✅ พบ Python3
python3 --version

REM ตรวจสอบและติดตั้ง dependencies
echo.
echo 📦 ตรวจสอบ dependencies...
pip3 install -r requirements.txt

if errorlevel 1 (
    echo ❌ ไม่สามารถติดตั้ง dependencies ได้
    echo ลองใช้: python3 -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies พร้อมใช้งาน

REM รันแอปพลิเคชัน
echo.
echo 🚀 เริ่มต้น Screen Translator...
echo.
cd src
python3 main.py

if errorlevel 1 (
    echo.
    echo ❌ เกิดข้อผิดพลาดในการรันแอปพลิเคชัน
    pause
)
