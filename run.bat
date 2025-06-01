@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo    Screen Translator - Real-time OCR
echo ========================================
echo.

REM Check if Python is available
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo Found Python:
    python --version
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        echo Found Python3:
        python3 --version
    ) else (
        echo ERROR: Python not found in system
        echo Please install Python 3.7+ from https://python.org
        echo Or add Python to your PATH environment variable
        pause
        exit /b 1
    )
)

REM Quick dependency check
echo.
echo Checking critical dependencies...
%PYTHON_CMD% -c "import PyQt5; print('PyQt5: OK')" 2>nul || (
    echo PyQt5 not found, will attempt to install...
    goto :install_deps
)
%PYTHON_CMD% -c "import cv2; print('OpenCV: OK')" 2>nul || (
    echo OpenCV not found, will attempt to install...
    goto :install_deps
)
echo Dependencies check passed
goto :run_app

:install_deps
echo.
echo Installing/updating dependencies...
%PYTHON_CMD% -m pip install --upgrade pip --user
%PYTHON_CMD% -m pip install PyQt5 opencv-python pytesseract deep-translator Pillow pyautogui numpy pywin32 pyperclip requests --user --upgrade

if %errorlevel% neq 0 (
    echo ERROR: Failed to install some dependencies
    echo Try running as administrator or check your internet connection
    echo You can also try: .\install.ps1 for more detailed installation
    pause
    exit /b 1
)

echo Dependencies installed successfully

:run_app
REM Run the application
echo.
echo Starting Screen Translator...
echo Press Ctrl+C to stop the application
echo.
cd src
%PYTHON_CMD% main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application failed to start
    echo.
    echo Troubleshooting tips:
    echo 1. Run install.ps1 to reinstall dependencies
    echo 2. Check if Tesseract OCR is installed
    echo 3. Make sure Python 3.7+ is properly installed
    cd ..
    pause
    exit /b 1
)

cd ..
echo.
echo Application closed normally
pause
