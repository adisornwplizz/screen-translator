# Makefile for Screen Translator (Windows with python3)
# Use with: make <target>

# Python command
PYTHON = python3
PIP = pip3

# Project directories
SRC_DIR = src
REQUIREMENTS = requirements.txt

# Default target
.PHONY: all
all: install run

# Install dependencies
.PHONY: install
install:
	@echo "📦 Installing Python dependencies..."
	$(PIP) install -r $(REQUIREMENTS)
	@echo "✅ Dependencies installed!"

# Alternative install using python module
.PHONY: install-alt
install-alt:
	@echo "📦 Installing dependencies using python3 module..."
	$(PYTHON) -m pip install -r $(REQUIREMENTS)
	@echo "✅ Dependencies installed!"

# Install Tesseract OCR (manual step)
.PHONY: install-tesseract
install-tesseract:
	@echo "🔧 Please manually install Tesseract OCR:"
	@echo "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki"
	@echo "2. Install to: C:\\Program Files\\Tesseract-OCR\\"
	@echo "3. Add to PATH: C:\\Program Files\\Tesseract-OCR\\"
	@echo "4. Restart terminal"

# Run the application
.PHONY: run
run:
	@echo "🚀 Starting Screen Translator..."
	cd $(SRC_DIR) && $(PYTHON) main.py

# Quick run using batch file
.PHONY: run-bat
run-bat:
	@echo "🚀 Running with batch file..."
	./run.bat

# Test OCR functionality
.PHONY: test-ocr
test-ocr:
	@echo "🧪 Testing OCR..."
	$(PYTHON) -c "import sys; sys.path.append('src'); from translation.ocr import OCR; ocr = OCR(); ocr.test_ocr()"

# Test translation functionality
.PHONY: test-translate
test-translate:
	@echo "🧪 Testing Translation..."
	$(PYTHON) -c "import sys; sys.path.append('src'); from translation.translator import Translator; t = Translator(); t.test_translation()"

# Check if all dependencies are available
.PHONY: check
check:
	@echo "🔍 Checking system requirements..."
	@echo "Python3 version:"
	@$(PYTHON) --version || echo "❌ Python3 not found!"
	@echo "Checking pip3:"
	@$(PIP) --version || echo "❌ pip3 not found!"
	@echo "Checking Tesseract..."
	@tesseract --version || echo "❌ Tesseract not found!"
	@echo "Checking Python packages..."
	@$(PYTHON) -c "import PyQt5; print('✅ PyQt5 available')" || echo "❌ PyQt5 not available"
	@$(PYTHON) -c "import cv2; print('✅ OpenCV available')" || echo "❌ OpenCV not available"
	@$(PYTHON) -c "import pytesseract; print('✅ Pytesseract available')" || echo "❌ Pytesseract not available"
	@$(PYTHON) -c "import googletrans; print('✅ Googletrans available')" || echo "❌ Googletrans not available"
	@$(PYTHON) -c "import pyautogui; print('✅ PyAutoGUI available')" || echo "❌ PyAutoGUI not available"

# Quick system info
.PHONY: info
info:
	@echo "💻 System Information:"
	@echo "Operating System: Windows"
	@echo "Python version:"
	@$(PYTHON) --version
	@echo "Python executable:"
	@where python3
	@echo "Current directory:"
	@cd

# Clean cache files
.PHONY: clean
clean:
	@echo "🧹 Cleaning cache files..."
	@if exist "__pycache__" rmdir /s /q __pycache__
	@if exist "src\\__pycache__" rmdir /s /q src\\__pycache__
	@if exist "src\\gui\\__pycache__" rmdir /s /q src\\gui\\__pycache__
	@if exist "src\\translation\\__pycache__" rmdir /s /q src\\translation\\__pycache__
	@if exist "src\\utils\\__pycache__" rmdir /s /q src\\utils\\__pycache__
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@for /r . %%i in (*.pyc) do @if exist "%%i" del "%%i"
	@echo "✅ Cache cleaned!"

# Setup virtual environment
.PHONY: venv
venv:
	@echo "🐍 Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "✅ Virtual environment created!"
	@echo "To activate: venv\\Scripts\\activate"
	@echo "To deactivate: deactivate"

# Install in virtual environment
.PHONY: venv-install
venv-install:
	@echo "📦 Installing in virtual environment..."
	@if not exist "venv" echo "❌ Virtual environment not found! Run 'make venv' first."
	@if exist "venv" venv\\Scripts\\pip.exe install -r $(REQUIREMENTS)
	@echo "✅ Dependencies installed in venv!"

# Run in virtual environment
.PHONY: venv-run
venv-run:
	@echo "🚀 Running in virtual environment..."
	@if not exist "venv" echo "❌ Virtual environment not found! Run 'make venv' first."
	@if exist "venv" venv\\Scripts\\python.exe $(SRC_DIR)\\main.py

# Update dependencies
.PHONY: update
update:
	@echo "🔄 Updating dependencies..."
	$(PIP) install --upgrade -r $(REQUIREMENTS)
	@echo "✅ Dependencies updated!"

# Create requirements.txt from current environment
.PHONY: freeze
freeze:
	@echo "📝 Creating requirements.txt..."
	$(PIP) freeze > requirements-freeze.txt
	@echo "✅ Requirements saved to requirements-freeze.txt"

# Development setup
.PHONY: dev-setup
dev-setup: venv venv-install
	@echo "🛠️ Development environment setup complete!"
	@echo "To start developing:"
	@echo "1. Activate venv: venv\\Scripts\\activate"
	@echo "2. Run app: make venv-run"

# Help
.PHONY: help
help:
	@echo "📚 Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the application"
	@echo "  make run-bat      - Run using batch file"
	@echo "  make check        - Check system requirements"
	@echo "  make test-ocr     - Test OCR functionality"
	@echo "  make test-translate - Test translation"
	@echo "  make clean        - Clean cache files"
	@echo "  make venv         - Create virtual environment"
	@echo "  make venv-run     - Run in virtual environment"
	@echo "  make dev-setup    - Setup development environment"
	@echo "  make info         - Show system information"
	@echo "  make help         - Show this help"

# Default help if no target specified
.DEFAULT_GOAL := help
