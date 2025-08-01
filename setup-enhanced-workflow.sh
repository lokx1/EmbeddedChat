#!/bin/bash

# Enhanced Workflow Builder Setup Script
# This script sets up the complete workflow builder system

set -e

echo "🚀 Setting up Enhanced Workflow Builder..."

# Backend Setup
echo "📦 Setting up backend..."

cd backend

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional dependencies for workflow engine
pip install aiohttp asyncio websockets celery redis

# Setup database
echo "Setting up database..."
python -c "from src.core.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "✅ Backend setup complete!"

# Frontend Setup
echo "📦 Setting up frontend..."

cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Install additional dependencies for enhanced features
npm install @types/ws ws

echo "✅ Frontend setup complete!"

# Create environment configuration
echo "📝 Creating environment configuration..."

cd ..

# Create backend .env file
cat > backend/.env << EOL
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/embedded_chat

# Redis Configuration (for caching and background tasks)
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Service API Keys (optional)
OPENAI_API_KEY=your-openai-api-key
CLAUDE_API_KEY=your-claude-api-key
GOOGLE_CREDENTIALS_PATH=path/to/google-credentials.json

# Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Slack Configuration (for notifications)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_DEFAULT_CHANNEL=#workflow-notifications

# Monitoring and Logging
LOG_LEVEL=INFO
ENABLE_METRICS=true
EOL

# Create frontend .env file
cat > frontend/.env << EOL
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# Feature Flags
VITE_ENABLE_ENHANCED_EDITOR=true
VITE_ENABLE_REAL_TIME_UPDATES=true
VITE_ENABLE_ANALYTICS=true

# Development Settings
VITE_LOG_LEVEL=debug
EOL

echo "✅ Environment configuration created!"

# Create startup scripts
echo "📜 Creating startup scripts..."

# Backend startup script
cat > start-backend.sh << 'EOL'
#!/bin/bash
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
EOL

# Frontend startup script
cat > start-frontend.sh << 'EOL'
#!/bin/bash
cd frontend
npm run dev
EOL

# Combined startup script
cat > start-all.sh << 'EOL'
#!/bin/bash

echo "🚀 Starting Enhanced Workflow Builder..."

# Start backend in background
echo "Starting backend..."
./start-backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
./start-frontend.sh &
FRONTEND_PID=$!

echo "✅ Both services started!"
echo "📍 Backend: http://localhost:8000"
echo "📍 Frontend: http://localhost:5173"
echo "📍 API Docs: http://localhost:8000/docs"

# Wait for user input to stop
echo "Press [CTRL+C] to stop all services..."
wait

# Clean up background processes
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
EOL

# Make scripts executable
chmod +x start-backend.sh start-frontend.sh start-all.sh

echo "✅ Startup scripts created!"

# Create development utilities
echo "🛠️ Creating development utilities..."

# Database reset script
cat > reset-database.sh << 'EOL'
#!/bin/bash
echo "⚠️  This will reset the entire database. Are you sure? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    cd backend
    python -c "
from src.core.database import engine, Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('✅ Database reset complete!')
"
    alembic stamp head
    echo "✅ Database migration stamp updated!"
else
    echo "❌ Database reset cancelled."
fi
EOL

# Test workflow creation script
cat > create-test-workflow.py << 'EOL'
#!/usr/bin/env python3
"""
Create a test workflow for development and testing
"""
import requests
import json

API_BASE = "http://localhost:8000/api/workflow"

def create_test_workflow():
    # Test workflow with HTTP request and data transform
    workflow_data = {
        "nodes": [
            {
                "id": "trigger-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "config": {"trigger_data": {"test": True}}
                }
            },
            {
                "id": "http-1",
                "type": "http_request",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Fetch Data",
                    "type": "http_request",
                    "config": {
                        "url": "https://jsonplaceholder.typicode.com/posts/1",
                        "method": "GET",
                        "timeout": 30
                    }
                }
            },
            {
                "id": "transform-1",
                "type": "data_transform",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "Transform Data",
                    "type": "data_transform",
                    "config": {
                        "transform_script": "// Transform the fetched data\nreturn { title: input.title, processed: true };"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "trigger-1",
                "target": "http-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            },
            {
                "id": "edge-2",
                "source": "http-1",
                "target": "transform-1",
                "sourceHandle": "success",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Create workflow instance
    instance_data = {
        "name": "Test HTTP Workflow",
        "workflow_data": workflow_data,
        "input_data": {"test_mode": True}
    }
    
    try:
        response = requests.post(f"{API_BASE}/instances", json=instance_data)
        response.raise_for_status()
        
        result = response.json()
        instance_id = result["instance_id"]
        
        print(f"✅ Test workflow created! Instance ID: {instance_id}")
        print(f"🌐 View in editor: http://localhost:5173/workflow/editor/{instance_id}")
        
        return instance_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create test workflow: {e}")
        return None

if __name__ == "__main__":
    instance_id = create_test_workflow()
    if instance_id:
        print("\n🚀 To execute this workflow:")
        print(f"curl -X POST {API_BASE}/instances/{instance_id}/execute")
EOL

chmod +x reset-database.sh
chmod +x create-test-workflow.py

echo "✅ Development utilities created!"

# Final instructions
cat << 'EOL'

🎉 Enhanced Workflow Builder setup complete!

📋 Next Steps:

1. Update configuration files:
   - backend/.env - Add your database credentials and API keys
   - frontend/.env - Adjust API endpoints if needed

2. Start the services:
   ./start-all.sh

3. Open your browser:
   - Frontend: http://localhost:5173
   - API Documentation: http://localhost:8000/docs
   - Workflow Editor: http://localhost:5173/workflow

4. Create a test workflow:
   python create-test-workflow.py

📚 Documentation:
   - Integration Guide: WORKFLOW_INTEGRATION_GUIDE.md
   - API Documentation: http://localhost:8000/docs
   - Component Development: See component_registry.py

🔧 Development Tools:
   - Reset Database: ./reset-database.sh
   - Create Test Data: python create-test-workflow.py

🚀 You're ready to build amazing workflows!

EOL

echo "✅ Setup script completed successfully!"
