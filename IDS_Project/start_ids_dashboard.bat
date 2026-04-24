@echo off
echo ===================================================
echo   IDS Neural Engine - Real Time Boot Sequence
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking and updating Python dependencies...
python -m pip install -r requirements.txt > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Make sure Python is added to your PATH.
    pause
    exit /b %errorlevel%
)

echo [2/3] Checking Machine Learning Models...
if not exist "models\rf_model.pkl" (
    echo Models not found! Generating initial training dataset. This will take a few seconds...
    python main.py --generate
    echo Training Random Forest AI Model...
    python main.py --train
)

echo [3/3] Launching OS Kernel Defense Matrix...
start http://127.0.0.1:5000
python app.py

pause
