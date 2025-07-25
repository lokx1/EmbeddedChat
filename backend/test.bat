@echo off
echo Running EmbeddedChat Backend Tests...
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

REM Run tests
echo Running pytest...
pytest tests/ -v --tb=short

echo.
echo Test run completed!
pause
