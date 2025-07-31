# Workflow Automation System

This is a complete workflow automation system built with React Flow frontend and FastAPI + LlamaIndex Workflow backend.

## Features

### Frontend
- Modern React Flow-based workflow editor
- Drag & drop interface for building automation workflows
- Real-time workflow execution monitoring
- Custom node types for different workflow steps
- Professional UI with dark/light theme support

### Backend
- LlamaIndex Workflow orchestration engine
- Multi-AI provider support (OpenAI, Claude, Ollama)
- Google Sheets and Google Drive integration
- Email and Slack notifications
- Analytics and reporting
- Background task execution
- RESTful API endpoints

## Workflow Capabilities

### Data Processing
- **Google Sheets Integration**: Read data from Google Sheets
- **AI Content Generation**: Generate content using OpenAI, Claude, or Ollama
- **File Storage**: Save outputs to Google Drive
- **Batch Processing**: Handle multiple rows of data concurrently

### Notifications
- **Email Notifications**: Send results via email
- **Slack Integration**: Post notifications to Slack channels
- **Real-time Updates**: WebSocket notifications for workflow status

### Analytics & Reporting
- **Execution Logs**: Detailed logs of all workflow executions
- **Performance Metrics**: Processing times, success rates, error tracking
- **Daily Reports**: Automated daily summary reports
- **Visual Analytics**: Charts and graphs for workflow performance

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL database
- Redis (for caching and rate limiting)

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Setup Database**
   ```bash
   # Create database tables
   python -m alembic upgrade head
   ```

4. **Start Backend Server**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

## Configuration

### AI Providers
Configure your AI provider API keys in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `CLAUDE_API_KEY`: Your Anthropic Claude API key
- `OLLAMA_BASE_URL`: URL to your Ollama instance

### Google Services
1. Create a Google Cloud project
2. Enable Google Sheets API and Google Drive API
3. Create service account credentials
4. Download credentials JSON file
5. Set `GOOGLE_CREDENTIALS_PATH` in `.env`

### Notifications
- **Email**: Configure SMTP settings in `.env`
- **Slack**: Create a Slack app and set bot token in `.env`

## API Endpoints

### Workflow Management
- `POST /api/workflow/templates` - Create workflow template
- `GET /api/workflow/templates` - List workflow templates
- `POST /api/workflow/instances` - Create workflow instance
- `POST /api/workflow/instances/{id}/execute` - Execute workflow

### Google Sheets Processing
- `POST /api/workflow/google-sheets/process` - Process Google Sheets data

### Analytics & Reporting
- `GET /api/workflow/analytics/daily` - Get daily analytics
- `GET /api/workflow/analytics/weekly` - Get weekly summary
- `POST /api/workflow/reports/daily` - Generate daily report

### Task Logs
- `GET /api/workflow/task-logs` - Get workflow execution logs

## Workflow Examples

### Basic Automation Workflow
1. **Input**: Google Sheets with data rows
2. **Processing**: Generate content using AI
3. **Output**: Save to Google Drive
4. **Notification**: Send email/Slack notification

### Daily Report Workflow
1. **Data Collection**: Gather execution metrics
2. **Analysis**: Calculate performance statistics
3. **Visualization**: Generate charts and graphs
4. **Distribution**: Email report to stakeholders

## Architecture

### Backend Components
- **WorkflowExecutor**: Main orchestration engine using LlamaIndex
- **AI Providers**: Abstracted AI service providers
- **Google Services**: Sheets and Drive integration
- **Notification Manager**: Email and Slack services
- **Analytics Service**: Metrics collection and reporting

### Frontend Components
- **WorkflowEditor**: React Flow-based editor
- **NodeTypes**: Custom nodes for workflow steps
- **WorkflowRunner**: Execution monitoring
- **Analytics Dashboard**: Performance visualization

## Deployment

### Docker Deployment
```bash
# Backend
cd backend
docker build -t workflow-backend .
docker run -p 8000:8000 workflow-backend

# Frontend
cd frontend
npm run build
# Deploy build folder to your web server
```

### Production Considerations
- Use environment-specific configuration
- Setup proper database connection pooling
- Configure Redis for production
- Setup proper logging and monitoring
- Use HTTPS in production
- Configure proper CORS settings

## Monitoring & Troubleshooting

### Logs
- Application logs are available in the backend console
- Workflow execution logs are stored in the database
- Access logs via `/api/workflow/task-logs` endpoint

### Health Checks
- Backend health: `GET /api/health`
- Database connectivity check included

### Common Issues
1. **AI Provider Errors**: Check API keys and rate limits
2. **Google API Errors**: Verify credentials and API permissions
3. **Database Connection**: Check PostgreSQL connection settings
4. **Redis Issues**: Verify Redis server is running

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## License

MIT License - see LICENSE file for details
