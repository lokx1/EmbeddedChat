# EmbeddedChat Workflow Automation System

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- PostgreSQL database
- Google Cloud credentials (for Sheets/Drive integration)
- AI Provider API keys (OpenAI, Claude, or Ollama)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Setup database:**
   ```bash
   # Create PostgreSQL database
   createdb embeddedchat
   
   # Run migrations
   alembic upgrade head
   ```

5. **Start backend server:**
   ```bash
   python main.py
   ```
   Backend will run on http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults should work for local development)
   ```

4. **Start frontend development server:**
   ```bash
   npm run dev
   ```
   Frontend will run on http://localhost:3000

## 🛠️ Configuration

### Backend Configuration (.env)

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `CLAUDE_API_KEY`: Claude API key (optional)
- `OLLAMA_BASE_URL`: Ollama server URL (optional, defaults to localhost:11434)
- `GOOGLE_CREDENTIALS_PATH`: Path to Google service account JSON file
- `SMTP_*`: Email configuration for notifications
- `SLACK_BOT_TOKEN`: Slack bot token for notifications

### Frontend Configuration (.env)

Optional environment variables:
- `VITE_API_BASE_URL`: Backend API URL (defaults to http://localhost:8000)

## 📋 Features

### ✅ Implemented Features

1. **Workflow Automation Engine**
   - LlamaIndex-based workflow orchestration
   - Event-driven architecture
   - Parallel task execution
   - State management

2. **AI Provider Integration**
   - OpenAI (GPT models, DALL-E, TTS)
   - Claude (text generation, vision)
   - Ollama (local LLM support)

3. **Google Services Integration**
   - Google Sheets reading/writing
   - Google Drive file storage
   - Batch data processing

4. **Notification System**
   - Email notifications (SMTP)
   - Slack notifications
   - Multi-channel support

5. **Analytics & Reporting**
   - Performance metrics
   - Success/failure rates
   - Daily/weekly reports
   - Visual charts and exports

6. **Modern Frontend Interface**
   - React Flow-based workflow editor
   - Real-time monitoring dashboard
   - Dark/light theme support
   - Responsive design

### 🎯 Usage Examples

#### 1. Basic Workflow Automation
1. Access the frontend at http://localhost:3000
2. Navigate to "Workflows" section
3. Create a new workflow instance
4. Configure Google Sheets input
5. Set AI processing parameters
6. Configure output destination
7. Execute workflow

#### 2. Google Sheets Processing
1. Go to "Google Sheets" tab in the dashboard
2. Enter your Google Sheets ID
3. Click "Process Sheets"
4. Monitor execution in real-time

#### 3. Analytics & Reports
1. Visit "Analytics" tab
2. View daily/weekly performance metrics
3. Generate custom reports
4. Download analytics data

## 🔧 API Endpoints

### Workflow Management
- `POST /api/v1/workflow/instances` - Create workflow instance
- `POST /api/v1/workflow/instances/{id}/execute` - Execute workflow
- `GET /api/v1/workflow/instances` - List workflow instances
- `GET /api/v1/workflow/instances/{id}` - Get workflow details

### Google Sheets
- `POST /api/v1/workflow/google-sheets/process` - Process Google Sheets

### Analytics
- `GET /api/v1/workflow/analytics/daily` - Get daily analytics
- `GET /api/v1/workflow/analytics/weekly` - Get weekly analytics
- `POST /api/v1/workflow/reports/daily` - Generate daily report

### Task Logs
- `GET /api/v1/workflow/task-logs` - Get execution logs

## 🐛 Troubleshooting

### Common Issues

1. **Backend connection failed**
   - Ensure backend is running on port 8000
   - Check database connection
   - Verify environment variables

2. **Google Services not working**
   - Check Google credentials file path
   - Verify Google APIs are enabled
   - Ensure proper permissions

3. **AI providers not responding**
   - Verify API keys are correct
   - Check network connectivity
   - For Ollama, ensure server is running

4. **Frontend build errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify TypeScript configuration

### Health Checks

- Backend health: http://localhost:8000/api/v1/health
- Frontend status: Check browser console for errors
- Database: Check PostgreSQL connection and tables

## 📚 Documentation

- Backend API docs: http://localhost:8000/api/docs
- LlamaIndex documentation: https://docs.llamaindex.ai/
- React Flow documentation: https://reactflow.dev/

## 🔒 Security Notes

- Never commit .env files to version control
- Use strong database passwords
- Secure API keys and credentials
- Enable HTTPS in production
- Implement proper authentication and authorization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
