@echo off
echo Installing frontend dependencies...
cd /d "%~dp0"
if not exist "node_modules" (
    echo Installing npm dependencies...
    npm install
) else (
    echo Dependencies already installed, skipping...
)

echo.
echo Frontend dependencies installed successfully!
echo.
echo To start the development server, run:
echo   npm run dev
echo.
pause
