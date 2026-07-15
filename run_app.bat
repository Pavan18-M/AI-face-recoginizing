@echo off
echo ===================================================
echo   AI Face Recognition Attendance System Launcher
echo ===================================================
echo.

:: Check if virtual environment exists
if not exist "venv\" (
    echo [ERROR] Virtual environment 'venv' not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Please install Python.
        pause
        exit /b
    )
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing/Verifying dependencies...
echo [INFO] This might take a few minutes for PyTorch and computer vision packages...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

echo [INFO] Initializing system database and launching application...
python app.py

echo.
echo [INFO] Application stopped.
pause
