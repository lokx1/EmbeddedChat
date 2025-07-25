@echo off
echo Installing EmbeddedChat Backend Dependencies...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Update .env file with your PostgreSQL credentials
echo 2. Test database connection: python setup_db.py test
echo 3. Create database tables: python setup_db.py create
echo 4. Run the application: python main.py
echo.
echo Current .env database settings:
type .env | findstr DATABASE_URL
echo.
pause
