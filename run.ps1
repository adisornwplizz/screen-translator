# Screen Translator PowerShell Launcher
# Run this script to start the Screen Translator application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Screen Translator - Real-time OCR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = $null
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -ge 3 -and $minor -ge 7) {
            $pythonCmd = "python"
            Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
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
                Write-Host "✅ Found Python3: $pythonVersion" -ForegroundColor Green
            } else {
                throw "Python version too old"
            }
        } else {
            throw "Cannot determine Python version"
        }
    } catch {
        Write-Host "❌ Python 3.7+ not found!" -ForegroundColor Red
        Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
        Write-Host "Or run the installation script: .\install.ps1" -ForegroundColor Cyan
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Quick dependency check
Write-Host ""
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
$missingDeps = @()

$requiredPackages = @("PyQt5", "opencv-python", "pytesseract", "deep-translator", "Pillow")
foreach ($package in $requiredPackages) {
    try {
        & $pythonCmd -c "import $($package.Replace('-', '_').Replace('opencv_python', 'cv2').Replace('deep_translator', 'deep_translator').Replace('PyQt5', 'PyQt5'))" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            $missingDeps += $package
        }
    } catch {
        $missingDeps += $package
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host "⚠️ Missing dependencies detected:" -ForegroundColor Yellow
    foreach ($dep in $missingDeps) {
        Write-Host "  - $dep" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Would you like to install missing dependencies? (y/n): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Installing missing dependencies..." -ForegroundColor Cyan
        foreach ($dep in $missingDeps) {
            & $pythonCmd -m pip install $dep --user --upgrade
        }
    } else {
        Write-Host "⚠️ Application may not work without all dependencies" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ All required dependencies found" -ForegroundColor Green
}

# Run the application
Write-Host ""
Write-Host "🚀 Starting Screen Translator..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

try {
    Push-Location src
    & $pythonCmd main.py
} catch {
    Write-Host ""
    Write-Host "❌ Application failed to start" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Run: .\install.ps1 to reinstall dependencies" -ForegroundColor Cyan
    Write-Host "2. Check if Tesseract OCR is installed" -ForegroundColor Cyan
    Write-Host "3. Make sure Python 3.7+ is properly installed" -ForegroundColor Cyan
} finally {
    Pop-Location
    Write-Host ""
    Read-Host "Press Enter to exit"
}
