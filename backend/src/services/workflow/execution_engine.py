"""
Enhanced Workflow Execution Engine with Real-time Updates
"""
import asyncio
import uuid
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from sqlalchemy.orm import Session

from ...models.workflow import WorkflowInstance, WorkflowExecutionStep
from ...schemas.workflow_components import ExecutionContext, ExecutionResult
from ...schemas.workflow_editor import WorkflowEditorData
from .component_registry import component_registry


class ExecutionEvent:
    """Represents an execution event for real-time updates"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], timestamp: datetime = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class WorkflowExecutionEngine:
    """Enhanced workflow execution engine with real-time updates"""
    
    def __init__(self, db: Session):
        self.db = db
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.event_callbacks: List[Callable[[str, ExecutionEvent], None]] = []
    
    def add_event_callback(self, callback: Callable[[str, ExecutionEvent], None]):
        """Add a callback for execution events"""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[str, ExecutionEvent], None]):
        """Remove an event callback"""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    def _emit_event(self, instance_id: str, event: ExecutionEvent):
        """Emit an event to all registered callbacks"""
        for callback in self.event_callbacks:
            try:
                callback(instance_id, event)
            except Exception as e:
                print(f"Error in event callback: {e}")
    
    async def execute_workflow(self, instance_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow instance"""
        
        # Get workflow instance from database
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if not instance:
            raise ValueError(f"Workflow instance {instance_id} not found")
        
        # Update instance status
        instance.status = "running"
        instance.started_at = datetime.now()
        
        # Use instance input_data if no input_data provided in execution call
        if not input_data and instance.input_data:
            input_data = instance.input_data
        elif input_data:
            # Update instance with new input_data
            instance.input_data = input_data
        
        instance.execution_logs = []
        self.db.commit()
        
        # Emit execution started event
        self._emit_event(instance_id, ExecutionEvent(
            "execution_started",
            {"instance_id": instance_id, "input_data": input_data}
        ))
        
        try:
            # Create execution task
            task = asyncio.create_task(
                self._execute_workflow_steps(instance, input_data or {})
            )
            self.active_executions[instance_id] = task
            
            # Wait for execution to complete
            result = await task
            
            # Update instance with results
            instance.status = "completed"
            instance.completed_at = datetime.now()
            instance.output_data = result
            self.db.commit()
            
            # Emit execution completed event
            self._emit_event(instance_id, ExecutionEvent(
                "execution_completed",
                {"instance_id": instance_id, "output_data": result}
            ))
            
            return result
            
        except Exception as e:
            # Update instance with error
            instance.status = "failed"
            instance.completed_at = datetime.now()
            instance.error_message = str(e)
            self.db.commit()
            
            # Emit execution failed event
            self._emit_event(instance_id, ExecutionEvent(
                "execution_failed",
                {"instance_id": instance_id, "error": str(e)}
            ))
            
            raise e
        
        finally:
            # Clean up
            if instance_id in self.active_executions:
                del self.active_executions[instance_id]
    
    async def _execute_workflow_steps(self, instance: WorkflowInstance, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps"""
        
        workflow_data = instance.workflow_data
        nodes = {node["id"]: node for node in workflow_data["nodes"]}
        edges = workflow_data["edges"]
        
        # Find trigger nodes (nodes with no incoming edges)
        incoming_edges = {edge["target"] for edge in edges}
        trigger_nodes = [node_id for node_id in nodes.keys() if node_id not in incoming_edges]
        
        if not trigger_nodes:
            raise ValueError("No trigger nodes found in workflow")
        
        # Build adjacency list for efficient traversal
        adjacency = {}
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append({
                "target": target,
                "source_handle": edge.get("sourceHandle"),
                "target_handle": edge.get("targetHandle")
            })
        
        # Track execution state
        executed_nodes = set()
        node_outputs = {}
        global_variables = {}
        
        # Execute trigger nodes first
        for trigger_node_id in trigger_nodes:
            if trigger_node_id not in executed_nodes:
                await self._execute_node(
                    instance.id,
                    trigger_node_id,
                    nodes[trigger_node_id],
                    input_data,
                    node_outputs,
                    global_variables,
                    executed_nodes,
                    adjacency
                )
        
        # Return final outputs
        return {
            "node_outputs": node_outputs,
            "global_variables": global_variables,
            "executed_nodes": list(executed_nodes)
        }
    
    async def _execute_node(
        self,
        instance_id: str,
        node_id: str,
        node: Dict[str, Any],
        workflow_input: Dict[str, Any],
        node_outputs: Dict[str, Any],
        global_variables: Dict[str, Any],
        executed_nodes: set,
        adjacency: Dict[str, List[Dict[str, Any]]]
    ):
        """Execute a single node"""
        
        if node_id in executed_nodes:
            return
        
        node_type = node["type"]
        node_data = node["data"]
        
        # Emit step started event
        self._emit_event(instance_id, ExecutionEvent(
            "step_started",
            {"node_id": node_id, "node_type": node_type, "node_data": node_data}
        ))
        
        # DEBUG: Log node config for GoogleSheetsWrite
        if node_type == "google_sheets_write":
            with open("d:/EmbeddedChat/frontend_execution_debug.log", "a", encoding="utf-8") as f:
                f.write(f"\n=== GOOGLE SHEETS WRITE NODE EXECUTION ===\n")
                f.write(f"Node ID: {node_id}\n")
                f.write(f"Node Type: {node_type}\n")
                f.write(f"Node Data: {json.dumps(node_data, indent=2, ensure_ascii=False)}\n")
                f.write(f"Config from node_data: {json.dumps(node_data.get('config', {}), indent=2, ensure_ascii=False)}\n")
                f.write(f"==========================================\n")
        
        try:
            # Get component for this node type
            component_class = component_registry.get_component(node_type)
            component = component_class()
            
            # Prepare execution context
            input_data = {**workflow_input, **node_data.get("config", {})}
            
            # DEBUG: Log execution context for GoogleSheetsWrite
            if node_type == "google_sheets_write":
                with open("d:/EmbeddedChat/frontend_execution_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"\n=== EXECUTION CONTEXT ===\n")
                    f.write(f"Input Data: {json.dumps(input_data, indent=2, ensure_ascii=False)}\n")
                    f.write(f"Previous Outputs: {json.dumps(node_outputs, indent=2, ensure_ascii=False)}\n")
                    f.write(f"Global Variables: {json.dumps(global_variables, indent=2, ensure_ascii=False)}\n")
                    f.write(f"========================\n")
            
            context = ExecutionContext(
                workflow_id=instance_id,
                instance_id=instance_id,
                step_id=node_id,
                input_data=input_data,
                previous_outputs=node_outputs,
                global_variables=global_variables
            )
            
            # Execute component
            result = await component.execute(context)
            
            # Store execution step in database
            step = WorkflowExecutionStep(
                id=str(uuid.uuid4()),
                workflow_instance_id=instance_id,
                step_name=node_data.get("label", node_type),
                step_type=node_type,
                input_data=input_data,
                output_data=result.output_data,
                status="completed" if result.success else "failed",
                error_message=result.error,
                execution_time_ms=result.execution_time_ms,
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
            
            self.db.add(step)
            self.db.commit()
            
            # Store node output
            node_outputs[node_id] = result.output_data
            executed_nodes.add(node_id)
            
            print(f"🔧 Node {node_id} executed successfully!")
            print(f"🔧 Output keys: {list(result.output_data.keys()) if isinstance(result.output_data, dict) else type(result.output_data)}")
            print(f"🔧 Current node_outputs keys: {list(node_outputs.keys())}")
            
            # Emit step completed event
            self._emit_event(instance_id, ExecutionEvent(
                "step_completed",
                {
                    "node_id": node_id,
                    "success": result.success,
                    "output_data": result.output_data,
                    "execution_time_ms": result.execution_time_ms,
                    "logs": result.logs
                }
            ))
            
            if result.success:
                # Execute next nodes based on successful execution
                if node_id in adjacency:
                    for next_connection in adjacency[node_id]:
                        # Check if this is the correct output handle
                        if not next_connection["source_handle"] or next_connection["source_handle"] in result.next_steps:
                            next_node_id = next_connection["target"]
                            next_node = self.db.query(WorkflowInstance).filter(
                                WorkflowInstance.id == instance_id
                            ).first().workflow_data["nodes"]
                            
                            next_node_obj = next((n for n in next_node if n["id"] == next_node_id), None)
                            if next_node_obj:
                                await self._execute_node(
                                    instance_id,
                                    next_node_id,
                                    next_node_obj,
                                    workflow_input,
                                    node_outputs,
                                    global_variables,
                                    executed_nodes,
                                    adjacency
                                )
            else:
                # Handle error case - could trigger error handlers
                print(f"Node {node_id} failed: {result.error}")
                
        except Exception as e:
            # Emit step failed event
            self._emit_event(instance_id, ExecutionEvent(
                "step_failed",
                {"node_id": node_id, "error": str(e)}
            ))
            raise e
    
    async def stop_execution(self, instance_id: str) -> bool:
        """Stop a running workflow execution"""
        if instance_id in self.active_executions:
            task = self.active_executions[instance_id]
            task.cancel()
            
            # Update instance status
            instance = self.db.query(WorkflowInstance).filter(
                WorkflowInstance.id == instance_id
            ).first()
            
            if instance:
                instance.status = "cancelled"
                instance.completed_at = datetime.now()
                self.db.commit()
                
                # Emit execution stopped event
                self._emit_event(instance_id, ExecutionEvent(
                    "execution_stopped",
                    {"instance_id": instance_id}
                ))
            
            return True
        
        return False
    
    def get_execution_status(self, instance_id: str) -> Dict[str, Any]:
        """Get current execution status"""
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()
        
        if not instance:
            return {"error": "Instance not found"}
        
        is_running = instance_id in self.active_executions
        
        return {
            "instance_id": instance_id,
            "status": instance.status,
            "is_running": is_running,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "error_message": instance.error_message
        }
