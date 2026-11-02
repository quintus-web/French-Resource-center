@echo off
title French Resource Center & Club Hub
color 1F

echo ====================================================
echo   Launching Centre de Ressources Francais...
echo ====================================================

:: 1. Navigate to the project directory
cd /d "C:\Users\user\OneDrive\Desktop\French records site"

:: 2. Activate virtual environment if present
if exist "venv\Scripts\activate.bat" (
    echo Activating venv...
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating .venv...
    call ".venv\Scripts\activate.bat"
) else (
    echo Using system Python installation...
)

:: 3. Wait 2 seconds and open the dashboard in the default browser
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000/lending/dashboard/"

:: 4. Start the Django server
echo Starting server on http://127.0.0.1:8000/ ...
echo Press Ctrl+C or close this window to stop the server.
python manage.py runserver 127.0.0.1:8000

pause