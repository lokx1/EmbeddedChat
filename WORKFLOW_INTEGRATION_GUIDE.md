# Enhanced Workflow Builder Integration Guide

## Overview

This implementation provides a complete workflow builder system with real-time execution monitoring and full front-end to back-end integration. The system includes:

- **Component-based workflow builder** with drag-and-drop interface
- **Real-time execution engine** with WebSocket updates
- **Comprehensive API** for workflow management
- **Enhanced state management** with React hooks
- **Security and validation** throughout the stack

## Architecture

### Backend Components

1. **Component Registry** (`component_registry.py`)
   - Manages all available workflow components
   - Provides metadata for UI rendering
   - Handles component validation and execution

2. **Execution Engine** (`execution_engine.py`)
   - Executes workflows with real-time updates
   - Manages execution state and logging
   - Supports parallel and sequential execution

3. **WebSocket Manager** (`websocket_manager.py`)
   - Provides real-time updates during execution
   - Manages multiple client connections
   - Handles connection lifecycle

4. **Enhanced API Routes** (`workflow.py`)
   - RESTful endpoints for all workflow operations
   - Component metadata endpoints
   - Real-time execution controls

### Frontend Components

1. **Enhanced API Service** (`enhancedWorkflowEditorApi.ts`)
   - Type-safe API communication
   - Real-time WebSocket integration
   - Comprehensive error handling

2. **React Hooks** (`useEnhancedWorkflow.ts`)
   - Component management hooks
   - Instance management hooks
   - Real-time execution hooks
   - Editor state management hooks

3. **Enhanced Workflow Editor** (`EnhancedWorkflowEditor.tsx`)
   - Drag-and-drop workflow builder
   - Real-time save and execute
   - Live execution monitoring

4. **Execution Panel** (`ExecutionPanel.tsx`)
   - Real-time execution monitoring
   - Event and log display
   - Status indicators

## API Endpoints

### Component Management
```
GET /api/workflow/components
GET /api/workflow/components/{component_type}
```

### Workflow Instance Management
```
POST /api/workflow/instances
GET /api/workflow/instances
GET /api/workflow/instances/{instance_id}
```

### Workflow Execution
```
POST /api/workflow/instances/{instance_id}/execute
POST /api/workflow/instances/{instance_id}/stop
GET /api/workflow/instances/{instance_id}/status
GET /api/workflow/instances/{instance_id}/logs
```

### Real-time Updates
```
WebSocket: ws://localhost:8000/api/workflow/ws/{instance_id}
```

### Editor-specific
```
POST /api/workflow/editor/save
GET /api/workflow/editor/load/{workflow_id}
GET /api/workflow/editor/list
```

## Usage Examples

### 1. Creating a New Workflow Component

```python
# Backend - Add new component
class EmailSenderComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="email_sender",
            name="Email Sender",
            description="Send emails with templates",
            category=ComponentCategory.OUTPUT_ACTIONS,
            icon="EnvelopeIcon",
            color="from-purple-500 via-purple-600 to-indigo-600",
            parameters=[
                ComponentParameter(
                    name="to_email",
                    label="To Email",
                    type=ParameterType.STRING,
                    required=True,
                    description="Recipient email address"
                ),
                ComponentParameter(
                    name="subject",
                    label="Subject",
                    type=ParameterType.STRING,
                    required=True,
                    description="Email subject line"
                ),
                ComponentParameter(
                    name="body",
                    label="Email Body",
                    type=ParameterType.TEXTAREA,
                    required=True,
                    description="Email content"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="success", type="source", position="right", label="Success"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        # Implementation here
        pass

# Register the component
component_registry.register_component(EmailSenderComponent)
```

### 2. Frontend - Using the Enhanced Editor

```tsx
import React from 'react';
import EnhancedWorkflowEditor from './components/WorkflowEditor/EnhancedWorkflowEditor';

function MyWorkflowApp() {
  return (
    <div className="h-screen">
      <EnhancedWorkflowEditor 
        workflowId="optional-existing-workflow-id"
        onBack={() => console.log('Navigate back')}
      />
    </div>
  );
}
```

### 3. Frontend - Managing Workflow Instances

```tsx
import { useWorkflowInstances, useWorkflowExecution } from './hooks/useEnhancedWorkflow';

function WorkflowManager() {
  const { instances, createInstance, fetchInstances } = useWorkflowInstances();
  const { executeWorkflow, executionStatus } = useWorkflowExecution();

  const handleCreateAndExecute = async () => {
    // Create new instance
    const result = await createInstance({
      name: "My Test Workflow",
      workflow_data: {
        nodes: [/* workflow nodes */],
        edges: [/* workflow edges */]
      }
    });

    if (result.success && result.data) {
      // Execute the instance
      await executeWorkflow(result.data.instance_id, { test: true });
    }
  };

  return (
    <div>
      <button onClick={handleCreateAndExecute}>
        Create and Execute Workflow
      </button>
      
      {executionStatus && (
        <div>Status: {executionStatus.status}</div>
      )}
    </div>
  );
}
```

### 4. Real-time Execution Monitoring

```tsx
import { useWorkflowExecution } from './hooks/useEnhancedWorkflow';

function ExecutionMonitor({ instanceId }: { instanceId: string }) {
  const {
    executionStatus,
    executionEvents,
    executionLogs,
    isConnected
  } = useWorkflowExecution(instanceId);

  return (
    <div>
      <div>Connection: {isConnected ? 'Connected' : 'Disconnected'}</div>
      <div>Status: {executionStatus?.status}</div>
      
      <div>Recent Events:</div>
      {executionEvents.slice(0, 5).map((event, index) => (
        <div key={index}>
          {event.event_type}: {JSON.stringify(event.data)}
        </div>
      ))}
    </div>
  );
}
```

## Security Considerations

### 1. Input Validation
- All component parameters are validated before execution
- SQL injection protection in database queries
- XSS protection in frontend components

### 2. Authentication & Authorization
```python
# Add to workflow routes
from ...core.auth import get_current_user

@router.post("/instances/{instance_id}/execute")
async def execute_workflow_instance(
    instance_id: str,
    current_user = Depends(get_current_user),  # Add auth
    # ... other parameters
):
    # Verify user has permission to execute this workflow
    pass
```

### 3. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/instances/{instance_id}/execute")
@limiter.limit("10/minute")  # Limit executions
async def execute_workflow_instance(request: Request, ...):
    pass
```

## Scalability Recommendations

### 1. Database Optimization
```python
# Add indexes for better performance
CREATE INDEX idx_workflow_instances_status ON workflow_instances(status);
CREATE INDEX idx_workflow_instances_created_by ON workflow_instances(created_by);
CREATE INDEX idx_execution_logs_instance_id ON workflow_task_logs(workflow_instance_id);
```

### 2. Redis for Caching
```python
import redis

# Cache component metadata
redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def get_cached_components():
    cached = redis_client.get('workflow_components')
    if cached:
        return json.loads(cached)
    
    components = component_registry.get_all_components()
    redis_client.setex('workflow_components', 3600, json.dumps(components))
    return components
```

### 3. Background Task Queue
```python
from celery import Celery

app = Celery('workflow_executor')

@app.task
def execute_workflow_async(instance_id: str, input_data: dict):
    # Execute workflow in background worker
    pass
```

## Error Handling Best Practices

### 1. Frontend Error Boundaries
```tsx
class WorkflowErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Workflow Error:', error, errorInfo);
    // Send to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong with the workflow editor.</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 2. Backend Error Handling
```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def execute_workflow_with_error_handling(instance_id: str):
    try:
        result = await execution_engine.execute_workflow(instance_id)
        return result
    except ValidationError as e:
        logger.error(f"Validation error in workflow {instance_id}: {e}")
        # Update instance with validation error
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        logger.error(f"Timeout in workflow {instance_id}: {e}")
        # Update instance with timeout error
        raise HTTPException(status_code=408, detail="Workflow execution timed out")
    except Exception as e:
        logger.error(f"Unexpected error in workflow {instance_id}: {e}")
        # Update instance with general error
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Testing Strategy

### 1. Component Testing
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_http_request_component():
    component = HttpRequestComponent()
    
    context = ExecutionContext(
        workflow_id="test_workflow",
        instance_id="test_instance",
        step_id="test_step",
        input_data={
            "url": "https://api.example.com/test",
            "method": "GET"
        },
        previous_outputs={},
        global_variables={}
    )
    
    result = await component.execute(context)
    
    assert result.success
    assert "status_code" in result.output_data
```

### 2. Integration Testing
```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import EnhancedWorkflowEditor from './EnhancedWorkflowEditor';

test('should save workflow successfully', async () => {
  render(<EnhancedWorkflowEditor />);
  
  // Add some nodes
  const sidebar = screen.getByText('Manual Trigger');
  fireEvent.dragStart(sidebar);
  
  const canvas = screen.getByTestId('workflow-canvas');
  fireEvent.drop(canvas);
  
  // Save workflow
  const saveButton = screen.getByText('Save');
  fireEvent.click(saveButton);
  
  await waitFor(() => {
    expect(screen.getByText('Workflow saved successfully!')).toBeInTheDocument();
  });
});
```

This comprehensive integration provides a production-ready workflow builder system with all the features you requested. The system is modular, scalable, and follows modern development best practices.
