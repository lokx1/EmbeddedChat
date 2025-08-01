# Enhanced Workflow Builder System

A complete workflow automation platform with visual workflow design, real-time execution monitoring, and comprehensive API integration.

![Workflow Builder](https://img.shields.io/badge/Workflow-Builder-blue.svg)
![React](https://img.shields.io/badge/React-18.x-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)

## 🌟 Features

### Visual Workflow Builder
- **Drag & Drop Interface**: Intuitive component-based workflow design
- **Real-time Collaboration**: Multiple users can work on workflows simultaneously
- **Component Library**: Extensive library of pre-built workflow components
- **Custom Components**: Easy-to-develop custom workflow components

### Real-time Execution Engine
- **Live Monitoring**: Real-time execution updates via WebSocket
- **Step-by-step Tracking**: Monitor each workflow step as it executes
- **Error Handling**: Comprehensive error reporting and recovery
- **Parallel Execution**: Support for parallel workflow branches

### Comprehensive API
- **RESTful Endpoints**: Complete CRUD operations for workflows
- **WebSocket Support**: Real-time updates and communication
- **Authentication**: Secure user authentication and authorization
- **Rate Limiting**: Built-in rate limiting and security features

### Enhanced UI/UX
- **Modern Design**: Clean, intuitive interface with dark/light mode
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Accessibility**: WCAG 2.1 AA compliant interface
- **State Management**: Efficient state management with React hooks

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+ and pip
- **PostgreSQL** 12+ (or SQLite for development)
- **Redis** 6+ (optional, for caching and background tasks)

### Installation

#### Option 1: Automatic Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd EmbeddedChat

# Run setup script
# On Windows:
setup-enhanced-workflow.bat

# On macOS/Linux:
chmod +x setup-enhanced-workflow.sh
./setup-enhanced-workflow.sh
```

#### Option 2: Manual Setup

1. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
pip install aiohttp asyncio websockets celery redis

# Setup database
python -c "from src.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
alembic upgrade head
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm install @types/ws ws
```

3. **Environment Configuration**
```bash
# Copy and configure environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit the files with your configuration
```

### Running the Application

```bash
# Start all services
./start-all.sh   # or start-all.bat on Windows

# Or start services individually
./start-backend.sh   # Backend: http://localhost:8000
./start-frontend.sh  # Frontend: http://localhost:5173
```

## 📖 Usage

### Creating Your First Workflow

1. **Open the Workflow Editor**
   ```
   http://localhost:5173/workflow
   ```

2. **Drag Components from Sidebar**
   - Start with a **Manual Trigger** component
   - Add processing components like **HTTP Request** or **Data Transform**
   - Connect components by dragging from output handles to input handles

3. **Configure Components**
   - Click on any component to open its configuration panel
   - Set parameters like URLs, data transformations, etc.

4. **Save and Execute**
   - Click **Save** to store your workflow
   - Click **Execute** to run it and see real-time results

### Example Workflow

```json
{
  "name": "Data Processing Pipeline",
  "nodes": [
    {
      "id": "trigger-1",
      "type": "manual_trigger",
      "position": {"x": 100, "y": 100},
      "data": {
        "label": "Start",
        "config": {"trigger_data": {"source": "api"}}
      }
    },
    {
      "id": "http-1",
      "type": "http_request",
      "position": {"x": 300, "y": 100},
      "data": {
        "label": "Fetch Data",
        "config": {
          "url": "https://api.example.com/data",
          "method": "GET",
          "headers": {"Authorization": "Bearer token"}
        }
      }
    },
    {
      "id": "transform-1",
      "type": "data_transform",
      "position": {"x": 500, "y": 100},
      "data": {
        "label": "Process Data",
        "config": {
          "transform_script": "return {processed: true, data: input.data}"
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
  ]
}
```

## 🔧 API Reference

### Workflow Components

```http
GET /api/workflow/components
GET /api/workflow/components/{component_type}
```

### Workflow Instances

```http
POST /api/workflow/instances
GET /api/workflow/instances
GET /api/workflow/instances/{instance_id}
PUT /api/workflow/instances/{instance_id}
DELETE /api/workflow/instances/{instance_id}
```

### Workflow Execution

```http
POST /api/workflow/instances/{instance_id}/execute
POST /api/workflow/instances/{instance_id}/stop
GET /api/workflow/instances/{instance_id}/status
GET /api/workflow/instances/{instance_id}/logs
```

### Real-time Updates

```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8000/api/workflow/ws/{instance_id}');

ws.onmessage = (event) => {
  const executionEvent = JSON.parse(event.data);
  console.log('Execution event:', executionEvent);
};
```

## 🧩 Available Components

### Triggers
- **Manual Trigger**: Start workflows manually
- **Schedule Trigger**: Time-based workflow execution
- **Webhook Trigger**: HTTP-triggered workflows

### Data Sources
- **HTTP Request**: Make API calls and web requests
- **Database Query**: Execute database queries
- **Google Sheets**: Read/write Google Sheets data
- **File Reader**: Read various file formats

### Processing
- **Data Transform**: JavaScript-based data transformation
- **AI Processing**: Integration with OpenAI, Claude, Ollama
- **Filter**: Conditional data filtering
- **Aggregation**: Data aggregation and summarization

### Control Flow
- **If/Condition**: Conditional workflow branching
- **Loop**: Iterate over data collections
- **Wait/Delay**: Add delays to workflows
- **Parallel**: Execute multiple branches simultaneously

### Output & Actions
- **Email Sender**: Send email notifications
- **Slack Notification**: Send Slack messages
- **File Writer**: Write data to files
- **Database Insert**: Insert data into databases
- **Webhook**: Send HTTP notifications

## 🛠️ Development

### Creating Custom Components

1. **Define Component Class**

```python
from ..schemas.workflow_components import (
    WorkflowComponentMetadata, 
    ExecutionContext, 
    ExecutionResult,
    ComponentCategory,
    ComponentParameter,
    ComponentHandle,
    ParameterType
)

class CustomComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="custom_component",
            name="Custom Component",
            description="Your custom component description",
            category=ComponentCategory.AI_PROCESSING,
            icon="CogIcon",
            color="from-purple-500 to-pink-500",
            parameters=[
                ComponentParameter(
                    name="input_text",
                    label="Input Text",
                    type=ParameterType.STRING,
                    required=True,
                    description="Text to process"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left")
            ],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        # Your component logic here
        input_text = context.input_data.get("input_text", "")
        
        # Process the input
        result = f"Processed: {input_text}"
        
        return ExecutionResult(
            success=True,
            output_data={"result": result},
            logs=["Custom processing completed"]
        )
```

2. **Register Component**

```python
from ..services.workflow.component_registry import component_registry

component_registry.register_component(CustomComponent)
```

### Frontend Integration

```tsx
import { useWorkflowComponents, useWorkflowExecution } from './hooks/useEnhancedWorkflow';

function MyWorkflowApp() {
  const { components } = useWorkflowComponents();
  const { executeWorkflow, executionStatus } = useWorkflowExecution();

  return (
    <div>
      {/* Your workflow UI */}
    </div>
  );
}
```

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
npm run test:integration
```

### Creating Test Workflows

```bash
# Create a test workflow
python create-test-workflow.py

# Execute test workflow via API
curl -X POST http://localhost:8000/api/workflow/instances/{instance_id}/execute
```

## 📊 Monitoring & Analytics

### Built-in Metrics
- Workflow execution times
- Success/failure rates
- Component usage statistics
- Performance monitoring

### Logging
- Structured JSON logging
- Execution audit trails
- Error tracking and reporting

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Workflow service health
curl http://localhost:8000/api/workflow/health
```

## 🔒 Security

### Authentication
- JWT-based authentication
- Role-based access control (RBAC)
- API key authentication for integrations

### Input Validation
- Comprehensive parameter validation
- SQL injection prevention
- XSS protection

### Rate Limiting
- API endpoint rate limiting
- Workflow execution limits
- Resource usage monitoring

## 📈 Performance & Scalability

### Optimization Features
- Database query optimization with indexes
- Redis caching for component metadata
- Background task processing with Celery
- WebSocket connection pooling

### Scaling Recommendations
- Horizontal scaling with load balancers
- Database read replicas
- Container orchestration (Docker/Kubernetes)
- CDN for static assets

## 🔧 Configuration

### Backend Configuration

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# External APIs
OPENAI_API_KEY=your-key
CLAUDE_API_KEY=your-key
```

### Frontend Configuration

```env
# API Endpoints
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# Feature Flags
VITE_ENABLE_ENHANCED_EDITOR=true
VITE_ENABLE_REAL_TIME_UPDATES=true
```

## 📚 Documentation

- **[Integration Guide](WORKFLOW_INTEGRATION_GUIDE.md)**: Complete development guide
- **[API Documentation](http://localhost:8000/docs)**: Interactive API docs
- **[Component Development](backend/src/services/workflow/component_registry.py)**: Creating custom components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript/Python coding standards
- Add tests for new features
- Update documentation
- Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check the integration guide and API docs
- **Issues**: Open GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions

### Common Issues

**Q: WebSocket connection fails**
A: Ensure the backend is running and check firewall settings

**Q: Database connection errors**
A: Verify PostgreSQL is running and credentials are correct

**Q: Components not loading**
A: Check the backend logs for component registration errors

### Performance Tips
- Use Redis for better caching performance
- Enable database indexes for large datasets
- Configure proper logging levels for production

---

## 🎉 Getting Started Checklist

- [ ] Install prerequisites (Node.js, Python, PostgreSQL)
- [ ] Run setup script (`setup-enhanced-workflow.bat/sh`)
- [ ] Configure environment files (`.env`)
- [ ] Start services (`start-all.bat/sh`)
- [ ] Open browser to `http://localhost:5173`
- [ ] Create your first workflow
- [ ] Explore the API docs at `http://localhost:8000/docs`

**Happy workflow building! 🚀**
