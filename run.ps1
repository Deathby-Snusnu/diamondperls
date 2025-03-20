Write-Host "Checking Python version..."

$pythonVersion = python --version 2>$null
if ($pythonVersion -notmatch "3.9" -and $pythonVersion -notmatch "3.[1-9]" -and $pythonVersion -notmatch "[4-9]\.") {
    Write-Host "Python 3.9 or higher is not installed. Please install the correct version."
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "Checking for virtual environment..."
if (-Not (Test-Path ".venv")) {
    Write-Host "No virtual environment found. Creating one..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment."
        Read-Host "Press Enter to exit"
        exit
    }
    Write-Host "Virtual environment created successfully."
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing requirements..."
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install requirements."
        Read-Host "Press Enter to exit"
        exit
    }
    Write-Host "Requirements installed successfully."
} else {
    Write-Host "No requirements.txt file found. Skipping requirements installation."
}

Write-Host "Starting the Diamond Perls Generator..."
python .\src\pearlsapp.py

