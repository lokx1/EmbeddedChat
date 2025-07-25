@echo off
echo Starting EmbeddedChat Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure your settings
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
echo Starting FastAPI server...
python main.py

pause
