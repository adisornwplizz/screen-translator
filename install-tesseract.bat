@echo off
echo ========================================
echo    Installing Tesseract OCR
echo ========================================
echo.

echo 📥 กำลังติดตั้ง Tesseract OCR...
echo.

REM ตรวจสอบว่ามี winget หรือไม่
winget --version >nul 2>&1
if errorlevel 1 (
    echo ❌ winget ไม่พบในระบบ
    echo กรุณาติดตั้ง Tesseract ด้วยตนเอง:
    echo.
    echo 1. ไปที่ https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. ดาวน์โหลด tesseract-ocr-w64-setup-v5.x.x.exe
    echo 3. ติดตั้งไปยัง C:\Program Files\Tesseract-OCR\
    echo 4. เพิ่ม PATH หรือแก้ไข config.py
    echo.
    pause
    exit /b 1
)

echo ✅ พบ winget
echo กำลังติดตั้ง Tesseract OCR...

winget install UB-Mannheim.TesseractOCR

if errorlevel 1 (
    echo ❌ ไม่สามารถติดตั้งด้วย winget ได้
    echo กรุณาติดตั้งด้วยตนเอง:
    echo.
    echo 1. ไปที่ https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. ดาวน์โหลด tesseract-ocr-w64-setup-v5.x.x.exe
    echo 3. ติดตั้งไปยัง C:\Program Files\Tesseract-OCR\
    echo 4. เพิ่ม PATH หรือแก้ไข config.py
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Tesseract OCR ติดตั้งสำเร็จ!
echo.

REM ตรวจสอบการติดตั้ง
tesseract --version
if errorlevel 1 (
    echo ⚠️  Tesseract ติดตั้งแล้วแต่ยังไม่อยู่ใน PATH
    echo กรุณาเปิด Command Prompt ใหม่หรือเพิ่ม PATH:
    echo C:\Program Files\Tesseract-OCR\
    echo.
    echo หรือแก้ไขไฟล์ src\config.py ให้ชี้ไปยัง:
    echo TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
) else (
    echo ✅ Tesseract พร้อมใช้งาน!
)

echo.
echo 🎉 การติดตั้งเสร็จสิ้น
echo ตอนนี้สามารถรัน run.bat ได้แล้ว
echo.
pause
