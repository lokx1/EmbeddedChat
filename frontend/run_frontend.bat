@echo off
echo Starting EmbeddedChat Frontend Development Server...
cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Dependencies not found. Installing...
    npm install
)

echo.
echo Starting development server on http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

npm run dev
