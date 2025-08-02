"""
Enhanced Workflow Execution Engine with Real-time Updates and Async Logging
"""
import asyncio
import uuid
import json
import time
import traceback
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ...models.workflow import WorkflowInstance, WorkflowExecutionStep, WorkflowTaskLog
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
    """Enhanced workflow execution engine with real-time updates and comprehensive logging"""
    
    def __init__(self, db: AsyncSession):
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
        """Execute a workflow instance with enhanced logging"""
        
        # Get workflow instance from database
        result = await self.db.execute(select(WorkflowInstance).where(WorkflowInstance.id == instance_id))
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise ValueError(f"Workflow instance {instance_id} not found")
        
        # Update instance status
        instance.status = "running"
        instance.started_at = datetime.now()
        instance.input_data = input_data or {}
        instance.execution_logs = []
        await self.db.commit()
        
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
            await self.db.commit()
            
            # Emit execution completed event
            self._emit_event(instance_id, ExecutionEvent(
                "execution_completed",
                {"instance_id": instance_id, "result": result}
            ))
            
            return result
            
        except Exception as e:
            # Update instance status
            instance.status = "failed"
            instance.completed_at = datetime.now()
            instance.error_message = str(e)
            await self.db.commit()
            
            # Emit execution failed event
            self._emit_event(instance_id, ExecutionEvent(
                "execution_failed",
                {"instance_id": instance_id, "error": str(e)}
            ))
            raise e
        
        finally:
            # Clean up active execution
            if instance_id in self.active_executions:
                del self.active_executions[instance_id]

    async def _execute_workflow_steps(self, instance: WorkflowInstance, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps with enhanced logging"""
        
        workflow_data = instance.workflow_data
        nodes = workflow_data.get("nodes", [])
        edges = workflow_data.get("edges", [])
        
        # Build adjacency list for workflow execution
        adjacency = {}
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            source_handle = edge.get("sourceHandle")
            target_handle = edge.get("targetHandle")
            
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append({
                "target": target,
                "source_handle": source_handle,
                "target_handle": target_handle
            })
        
        # Find start nodes (nodes with no incoming edges)
        all_targets = {edge.get("target") for edge in edges}
        start_nodes = [node for node in nodes if node.get("id") not in all_targets]
        
        # If no start nodes found, look for manual trigger nodes
        if not start_nodes:
            start_nodes = [node for node in nodes if node.get("type") == "manual_trigger"]
        
        # If still no start nodes, use the first node
        if not start_nodes and nodes:
            start_nodes = [nodes[0]]
        
        # Initialize execution state
        node_outputs = {}
        global_variables = {}
        executed_nodes = set()
        
        # Execute start nodes
        for start_node in start_nodes:
            await self._execute_node(
                instance.id,
                start_node.get("id"),
                start_node,
                workflow_input,
                node_outputs,
                global_variables,
                executed_nodes,
                adjacency
            )
        
        return {
            "node_outputs": node_outputs,
            "global_variables": global_variables,
            "executed_nodes": list(executed_nodes)
        }

    async def _execute_node(self, instance_id: str, node_id: str, node_data: Dict[str, Any], 
                           workflow_input: Dict[str, Any], node_outputs: Dict[str, Any],
                           global_variables: Dict[str, Any], executed_nodes: set,
                           adjacency: Dict[str, List[Dict[str, Any]]]):
        """Execute a single node with comprehensive logging"""
        
        # Skip if already executed
        if node_id in executed_nodes:
            return
        
        node_type = node_data.get("type", "unknown")
        
        # Emit step started event
        self._emit_event(instance_id, ExecutionEvent(
            "step_started",
            {"node_id": node_id, "node_type": node_type, "node_data": node_data}
        ))
        
        try:
            # Get component for this node type
            component_class = component_registry.get_component(node_type)
            component = component_class()
            
            # Prepare execution context
            input_data = {**workflow_input, **node_data.get("data", {}).get("config", {})}
            
            # Create detailed task log
            task_log = WorkflowTaskLog(
                id=str(uuid.uuid4()),
                workflow_instance_id=instance_id,
                task_id=f"{instance_id}_{node_id}",
                task_name=node_data.get("data", {}).get("label", node_type),
                task_type=node_type,
                status="processing",
                log_level="INFO",
                input_data=input_data,
                expected_output={"success": True, "output_data": {}},
                success_criteria={"required_fields": [], "validation_rules": []},
                user_id=workflow_input.get("user_id"),
                session_id=workflow_input.get("session_id"),
                correlation_id=f"{instance_id}_{datetime.now().timestamp()}",
                tags={"node_type": node_type, "execution_batch": instance_id},
                context={"node_config": node_data.get("data", {}).get("config", {}), "previous_outputs_count": len(node_outputs)},
                started_at=datetime.now()
            )
            
            self.db.add(task_log)
            await self.db.commit()
            
            context = ExecutionContext(
                workflow_id=instance_id,
                instance_id=instance_id,
                step_id=node_id,
                input_data=input_data,
                previous_outputs=node_outputs,
                global_variables=global_variables
            )
            
            # Execute component with timing
            start_time = time.time()
            result = await component.execute(context)
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Update task log with results
            task_log.status = "success" if result.success else "failed"
            task_log.output_data = result.output_data
            task_log.processing_time_ms = execution_time_ms
            task_log.completed_at = datetime.now()
            
            if not result.success:
                task_log.failure_reason = result.error
                task_log.error_code = "COMPONENT_EXECUTION_FAILED"
                task_log.log_level = "ERROR"
            
            # Handle Google Sheets specific logging
            if node_type == "google_sheets_write":
                sheet_config = node_data.get("data", {}).get("config", {})
                task_log.sheet_id = sheet_config.get("spreadsheet_id")
                if result.success and result.output_data:
                    task_log.api_response_code = 200
                    # Try to extract row information from output
                    if "rows_written" in result.output_data:
                        task_log.row_number = result.output_data.get("rows_written", 0)
                elif not result.success:
                    task_log.api_response_code = 400
                    task_log.error_code = "GOOGLE_SHEETS_WRITE_FAILED"
            
            # Handle AI processing specific logging
            elif node_type == "ai_processing":
                ai_config = node_data.get("data", {}).get("config", {})
                task_log.api_endpoint = f"ollama/{ai_config.get('model', 'unknown')}"
                if result.success:
                    task_log.api_response_code = 200
                    # Log token counts or processing metrics if available
                    if "token_count" in result.output_data:
                        task_log.context = {**task_log.context, "tokens_processed": result.output_data["token_count"]}
                else:
                    task_log.api_response_code = 500
                    task_log.error_code = "AI_PROCESSING_FAILED"
            
            await self.db.commit()
            
            # Store execution step in database (enhanced)
            step = WorkflowExecutionStep(
                id=str(uuid.uuid4()),
                workflow_instance_id=instance_id,
                step_name=node_data.get("data", {}).get("label", node_type),
                step_type=node_type,
                input_data=input_data,
                output_data=result.output_data,
                status="completed" if result.success else "failed",
                error_message=result.error,
                execution_time_ms=execution_time_ms,
                log_level="INFO" if result.success else "ERROR",
                component_version=getattr(component, 'version', '1.0.0'),
                user_id=workflow_input.get("user_id"),
                tags={"node_type": node_type, "task_log_id": task_log.id},
                metrics={"execution_time_ms": execution_time_ms, "success": result.success},
                dependencies=list(node_outputs.keys()) if node_outputs else [],
                artifacts={"output_keys": list(result.output_data.keys()) if result.output_data else []},
                started_at=task_log.started_at,
                completed_at=task_log.completed_at
            )
            
            self.db.add(step)
            await self.db.commit()
            
            # Store node output
            node_outputs[node_id] = result.output_data
            executed_nodes.add(node_id)
            
            # Emit step completed event
            self._emit_event(instance_id, ExecutionEvent(
                "step_completed",
                {
                    "node_id": node_id,
                    "success": result.success,
                    "output_data": result.output_data,
                    "execution_time_ms": execution_time_ms,
                    "logs": result.logs,
                    "task_log_id": task_log.id
                }
            ))
            
            if result.success:
                # Execute next nodes based on successful execution
                if node_id in adjacency:
                    for next_connection in adjacency[node_id]:
                        # Check if this is the correct output handle
                        if not next_connection["source_handle"] or next_connection["source_handle"] in result.next_steps:
                            next_node_id = next_connection["target"]
                            # Get workflow instance to access updated workflow data
                            instance_result = await self.db.execute(select(WorkflowInstance).where(WorkflowInstance.id == instance_id))
                            current_instance = instance_result.scalar_one()
                            next_node = next((n for n in current_instance.workflow_data["nodes"] if n["id"] == next_node_id), None)
                            
                            if next_node:
                                await self._execute_node(
                                    instance_id,
                                    next_node_id,
                                    next_node,
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
            # Update task log with error details
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            # Try to update existing task log if it exists
            try:
                existing_log = (await self.db.execute(
                    select(WorkflowTaskLog).where(WorkflowTaskLog.task_id == f"{instance_id}_{node_id}")
                )).scalar_one_or_none()
                
                if existing_log:
                    existing_log.status = "failed"
                    existing_log.failure_reason = error_message
                    existing_log.error_stack_trace = stack_trace
                    existing_log.error_code = "EXECUTION_EXCEPTION"
                    existing_log.log_level = "CRITICAL"
                    existing_log.completed_at = datetime.now()
                    if existing_log.started_at:
                        execution_time = (datetime.now() - existing_log.started_at).total_seconds() * 1000
                        existing_log.processing_time_ms = int(execution_time)
                else:
                    # Create new error log if none exists
                    error_log = WorkflowTaskLog(
                        id=str(uuid.uuid4()),
                        workflow_instance_id=instance_id,
                        task_id=f"{instance_id}_{node_id}_error",
                        task_name=f"ERROR: {node_data.get('data', {}).get('label', node_type)}",
                        task_type=node_type,
                        status="failed",
                        log_level="CRITICAL",
                        failure_reason=error_message,
                        error_stack_trace=stack_trace,
                        error_code="EXECUTION_EXCEPTION",
                        input_data=workflow_input,
                        started_at=datetime.now(),
                        completed_at=datetime.now()
                    )
                    self.db.add(error_log)
                
                await self.db.commit()
            except Exception as log_error:
                print(f"Failed to log error details: {log_error}")
            
            # Emit step failed event
            self._emit_event(instance_id, ExecutionEvent(
                "step_failed",
                {"node_id": node_id, "error": error_message, "stack_trace": stack_trace}
            ))
            raise e

    async def stop_execution(self, instance_id: str) -> bool:
        """Stop a running workflow execution"""
        if instance_id in self.active_executions:
            task = self.active_executions[instance_id]
            task.cancel()
            
            # Update instance status
            result = await self.db.execute(select(WorkflowInstance).where(WorkflowInstance.id == instance_id))
            instance = result.scalar_one_or_none()
            if instance:
                instance.status = "cancelled"
                instance.completed_at = datetime.now()
                await self.db.commit()
            
            # Clean up
            del self.active_executions[instance_id]
            
            return True
        return False

    def get_active_executions(self) -> List[str]:
        """Get list of currently active execution instance IDs"""
        return list(self.active_executions.keys())

    async def get_execution_status(self, instance_id: str) -> Optional[str]:
        """Get execution status for a workflow instance"""
        result = await self.db.execute(select(WorkflowInstance).where(WorkflowInstance.id == instance_id))
        instance = result.scalar_one_or_none()
        return instance.status if instance else None
