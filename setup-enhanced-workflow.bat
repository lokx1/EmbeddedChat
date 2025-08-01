@echo off
REM Enhanced Workflow Builder Setup Script for Windows
REM This script sets up the complete workflow builder system

echo 🚀 Setting up Enhanced Workflow Builder...

REM Backend Setup
echo 📦 Setting up backend...

cd backend

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Install additional dependencies for workflow engine
pip install aiohttp asyncio websockets celery redis

REM Setup database
echo Setting up database...
python -c "from src.core.database import engine, Base; Base.metadata.create_all(bind=engine)"

REM Run migrations
echo Running database migrations...
alembic upgrade head

echo ✅ Backend setup complete!

REM Frontend Setup
echo 📦 Setting up frontend...

cd ..\frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

REM Install additional dependencies for enhanced features
npm install @types/ws ws

echo ✅ Frontend setup complete!

REM Create environment configuration
echo 📝 Creating environment configuration...

cd ..

REM Create backend .env file
(
echo # Database Configuration
echo DATABASE_URL=postgresql://username:password@localhost:5432/embedded_chat
echo.
echo # Redis Configuration ^(for caching and background tasks^)
echo REDIS_URL=redis://localhost:6379/0
echo.
echo # API Configuration
echo API_HOST=0.0.0.0
echo API_PORT=8000
echo API_WORKERS=4
echo.
echo # Security
echo SECRET_KEY=your-secret-key-change-this-in-production
echo ALGORITHM=HS256
echo ACCESS_TOKEN_EXPIRE_MINUTES=30
echo.
echo # External Service API Keys ^(optional^)
echo OPENAI_API_KEY=your-openai-api-key
echo CLAUDE_API_KEY=your-claude-api-key
echo GOOGLE_CREDENTIALS_PATH=path/to/google-credentials.json
echo.
echo # Email Configuration ^(for notifications^)
echo SMTP_SERVER=smtp.gmail.com
echo SMTP_PORT=587
echo SMTP_USERNAME=your-email@gmail.com
echo SMTP_PASSWORD=your-app-password
echo.
echo # Slack Configuration ^(for notifications^)
echo SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
echo SLACK_DEFAULT_CHANNEL=#workflow-notifications
echo.
echo # Monitoring and Logging
echo LOG_LEVEL=INFO
echo ENABLE_METRICS=true
) > backend\.env

REM Create frontend .env file
(
echo # API Configuration
echo VITE_API_BASE_URL=http://localhost:8000
echo VITE_WS_BASE_URL=ws://localhost:8000
echo.
echo # Feature Flags
echo VITE_ENABLE_ENHANCED_EDITOR=true
echo VITE_ENABLE_REAL_TIME_UPDATES=true
echo VITE_ENABLE_ANALYTICS=true
echo.
echo # Development Settings
echo VITE_LOG_LEVEL=debug
) > frontend\.env

echo ✅ Environment configuration created!

REM Create startup scripts
echo 📜 Creating startup scripts...

REM Backend startup script
(
echo @echo off
echo cd backend
echo set PYTHONPATH=%%PYTHONPATH%%;%%cd%%
echo uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
) > start-backend.bat

REM Frontend startup script
(
echo @echo off
echo cd frontend
echo npm run dev
) > start-frontend.bat

REM Combined startup script
(
echo @echo off
echo echo 🚀 Starting Enhanced Workflow Builder...
echo.
echo REM Start backend in background
echo echo Starting backend...
echo start "Backend" cmd /k start-backend.bat
echo.
echo REM Wait a moment for backend to start
echo timeout /t 5 /nobreak
echo.
echo REM Start frontend
echo echo Starting frontend...
echo start "Frontend" cmd /k start-frontend.bat
echo.
echo echo ✅ Both services started!
echo echo 📍 Backend: http://localhost:8000
echo echo 📍 Frontend: http://localhost:5173
echo echo 📍 API Docs: http://localhost:8000/docs
echo.
echo echo Press any key to exit...
echo pause
) > start-all.bat

echo ✅ Startup scripts created!

REM Create development utilities
echo 🛠️ Creating development utilities...

REM Database reset script
(
echo @echo off
echo echo ⚠️  This will reset the entire database. Are you sure? ^(y/N^)
echo set /p response=
echo if /i "%%response%%" equ "y" ^(
echo     cd backend
echo     python -c "from src.core.database import engine, Base; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); print('✅ Database reset complete!')"
echo     alembic stamp head
echo     echo ✅ Database migration stamp updated!
echo ^) else ^(
echo     echo ❌ Database reset cancelled.
echo ^)
echo pause
) > reset-database.bat

echo ✅ Development utilities created!

REM Final instructions
echo.
echo 🎉 Enhanced Workflow Builder setup complete!
echo.
echo 📋 Next Steps:
echo.
echo 1. Update configuration files:
echo    - backend\.env - Add your database credentials and API keys
echo    - frontend\.env - Adjust API endpoints if needed
echo.
echo 2. Start the services:
echo    start-all.bat
echo.
echo 3. Open your browser:
echo    - Frontend: http://localhost:5173
echo    - API Documentation: http://localhost:8000/docs
echo    - Workflow Editor: http://localhost:5173/workflow
echo.
echo 📚 Documentation:
echo    - Integration Guide: WORKFLOW_INTEGRATION_GUIDE.md
echo    - API Documentation: http://localhost:8000/docs
echo.
echo 🔧 Development Tools:
echo    - Reset Database: reset-database.bat
echo.
echo 🚀 You're ready to build amazing workflows!
echo.

echo ✅ Setup script completed successfully!
pause
