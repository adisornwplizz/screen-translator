# Screen Translator Installation Script for Windows
# This script will install all required dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Screen Translator - Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonCmd = $null
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -ge 3 -and $minor -ge 7) {
            $pythonCmd = "python"
            Write-Host "✅ Found compatible Python: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python version too old"
        }
    } else {
        throw "Cannot determine Python version"
    }
} catch {
    try {
        $pythonVersion = python3 --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 7) {
                $pythonCmd = "python3"
                Write-Host "✅ Found compatible Python3: $pythonVersion" -ForegroundColor Green
            } else {
                throw "Python version too old"
            }
        } else {
            throw "Cannot determine Python version"
        }
    } catch {
        Write-Host "❌ Python 3.7+ not found!" -ForegroundColor Red
        Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Upgrade pip first
Write-Host ""
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
try {
    & $pythonCmd -m pip install --upgrade pip --user
    Write-Host "✅ pip upgraded successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not upgrade pip, continuing..." -ForegroundColor Yellow
}

# Install dependencies one by one with better error handling
$dependencies = @(
    "PyQt5",
    "opencv-python", 
    "pytesseract",
    "deep-translator",
    "Pillow",
    "pyautogui",
    "numpy",
    "pywin32",
    "pyperclip",
    "requests"
)

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow

$failed = @()
foreach ($dep in $dependencies) {
    Write-Host "Installing $dep..." -ForegroundColor Cyan
    try {
        & $pythonCmd -m pip install $dep --user --upgrade
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $dep installed successfully" -ForegroundColor Green
        } else {
            throw "pip returned error code $LASTEXITCODE"
        }
    } catch {
        Write-Host "❌ Failed to install $dep" -ForegroundColor Red
        $failed += $dep
    }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️ Some dependencies failed to install:" -ForegroundColor Yellow
    foreach ($dep in $failed) {
        Write-Host "  - $dep" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "You can try installing them manually with:" -ForegroundColor Yellow
    Write-Host "  $pythonCmd -m pip install <package_name> --user" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✅ All dependencies installed successfully!" -ForegroundColor Green
}

# Check if Tesseract is installed
Write-Host ""
Write-Host "🔍 Checking Tesseract OCR..." -ForegroundColor Yellow
try {
    tesseract --version | Out-Null
    Write-Host "✅ Tesseract is installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Tesseract OCR not found" -ForegroundColor Yellow
    Write-Host "OCR functionality may not work properly" -ForegroundColor Yellow
    Write-Host "You can install it from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    Write-Host "Or run: .\install-tesseract.bat" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "You can now run the application with: .\run.ps1" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
