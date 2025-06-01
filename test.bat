@echo off
echo Testing Screen Translator...
echo.

echo Testing Python availability...
python --version
if %errorlevel% neq 0 (
    echo Python not found with 'python' command
    python3 --version
    if %errorlevel% neq 0 (
        echo Python3 also not found
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

echo.
echo Testing PyQt5...
%PYTHON_CMD% -c "import PyQt5; print('PyQt5: OK')"
if %errorlevel% neq 0 (
    echo PyQt5 not available
    pause
    exit /b 1
)

echo.
echo Testing application startup...
cd src
%PYTHON_CMD% -c "from gui.window import Window; print('Application imports: OK')"
if %errorlevel% neq 0 (
    echo Application imports failed
    cd ..
    pause
    exit /b 1
)

cd ..
echo.
echo All tests passed! You can now run the application.
echo Use: run.bat or run.ps1
pause
