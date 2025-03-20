@echo off
echo Checking Python version...

python --version 2>NUL | findstr "3.9" >NUL
if errorlevel 1 (
    echo Python 3.9 is not installed. Please install the correct version.
    pause
    exit /b
)

echo Checking for virtual environment...
if not exist ".venv-diamond_perls" (
    echo No virtual environment found. Creating one...
    python -m venv .venv-diamond_perls
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b
    )
    echo Virtual environment created successfully.
)

echo Activating virtual environment...
call .venv-diamond_perls\Scripts\activate

echo Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements.
        pause
        exit /b
    )
    echo Requirements installed successfully.
) else (
    echo No requirements.txt file found. Skipping requirements installation.
)

echo Starting the Diamond Perls Generator...
python .\src\pearlsapp.py
pause