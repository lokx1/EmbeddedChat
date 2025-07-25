@echo off
echo EmbeddedChat Database Setup
echo ===========================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Current database configuration:
type .env | findstr DATABASE_URL
echo.

echo Please make sure:
echo 1. PostgreSQL is running
echo 2. Database 'EmbeddedAI' exists
echo 3. Username and password in .env are correct
echo.

echo Testing database connection...
python setup_db.py test

if errorlevel 1 (
    echo.
    echo Database connection failed!
    echo Please check your .env configuration and try again.
    pause
    exit /b 1
)

echo.
echo Creating database tables...
python setup_db.py create

if errorlevel 1 (
    echo.
    echo Failed to create tables!
    pause
    exit /b 1
)

echo.
echo ✅ Database setup completed successfully!
echo You can now run the application with: run.bat
echo.
pause
