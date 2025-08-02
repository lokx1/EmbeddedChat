"""
WebSocket handler for real-time workflow execution updates
"""
import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from .execution_engine_new import ExecutionEvent


class WorkflowWebSocketManager:
    """Manager for WebSocket connections for workflow updates"""
    
    def __init__(self):
        # Store active connections: workflow_instance_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection to instance mapping for cleanup
        self.connection_instances: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, instance_id: str):
        """Connect a websocket to a workflow instance"""
        await websocket.accept()
        
        if instance_id not in self.active_connections:
            self.active_connections[instance_id] = set()
        
        self.active_connections[instance_id].add(websocket)
        self.connection_instances[websocket] = instance_id
        
        print(f"WebSocket connected for workflow instance: {instance_id}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket"""
        if websocket in self.connection_instances:
            instance_id = self.connection_instances[websocket]
            
            # Remove from active connections
            if instance_id in self.active_connections:
                self.active_connections[instance_id].discard(websocket)
                
                # Clean up empty sets
                if not self.active_connections[instance_id]:
                    del self.active_connections[instance_id]
            
            # Remove from connection mapping
            del self.connection_instances[websocket]
            
            print(f"WebSocket disconnected for workflow instance: {instance_id}")
    
    async def send_event(self, instance_id: str, event: ExecutionEvent):
        """Send an event to all connected websockets for an instance"""
        if instance_id in self.active_connections:
            message = json.dumps(event.to_dict())
            
            # Create list to avoid modifying set during iteration
            connections = list(self.active_connections[instance_id])
            
            for websocket in connections:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    print(f"Error sending WebSocket message: {e}")
                    # Remove problematic connection
                    self.disconnect(websocket)
    
    async def send_custom_message(self, instance_id: str, message: Dict):
        """Send a custom message to all connected websockets for an instance"""
        if instance_id in self.active_connections:
            message_with_timestamp = {
                **message,
                "timestamp": datetime.now().isoformat()
            }
            
            message_json = json.dumps(message_with_timestamp)
            connections = list(self.active_connections[instance_id])
            
            for websocket in connections:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    print(f"Error sending WebSocket message: {e}")
                    self.disconnect(websocket)
    
    def get_connection_count(self, instance_id: str) -> int:
        """Get number of active connections for an instance"""
        return len(self.active_connections.get(instance_id, set()))
    
    def get_all_instances(self) -> Set[str]:
        """Get all instance IDs with active connections"""
        return set(self.active_connections.keys())


# Global WebSocket manager instance
websocket_manager = WorkflowWebSocketManager()


async def handle_websocket_connection(websocket: WebSocket, instance_id: str):
    """Handle a WebSocket connection for workflow updates"""
    try:
        await websocket_manager.connect(websocket, instance_id)
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "event_type": "connection_established",
            "data": {"instance_id": instance_id},
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client messages (like ping/pong, subscription changes, etc.)
                await handle_client_message(websocket, instance_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                # Send error for invalid JSON
                await websocket.send_text(json.dumps({
                    "event_type": "error",
                    "data": {"error": "Invalid JSON format"},
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                print(f"Error handling WebSocket message: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        websocket_manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, instance_id: str, message: Dict):
    """Handle messages from the client"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        await websocket.send_text(json.dumps({
            "event_type": "pong",
            "data": {"timestamp": datetime.now().isoformat()},
            "timestamp": datetime.now().isoformat()
        }))
    
    elif message_type == "subscribe_logs":
        # Client wants to subscribe to detailed logs
        await websocket.send_text(json.dumps({
            "event_type": "subscription_confirmed",
            "data": {"subscription": "logs", "instance_id": instance_id},
            "timestamp": datetime.now().isoformat()
        }))
    
    elif message_type == "get_status":
        # Client requests current execution status
        # This would integrate with the execution engine
        await websocket.send_text(json.dumps({
            "event_type": "status_response",
            "data": {"instance_id": instance_id, "status": "requested"},
            "timestamp": datetime.now().isoformat()
        }))
    
    else:
        # Unknown message type
        await websocket.send_text(json.dumps({
            "event_type": "error",
            "data": {"error": f"Unknown message type: {message_type}"},
            "timestamp": datetime.now().isoformat()
        }))


def execution_event_callback(instance_id: str, event: ExecutionEvent):
    """Callback function to handle execution events and send them via WebSocket"""
    # This will be called by the execution engine
    # We need to run it in the event loop
    asyncio.create_task(websocket_manager.send_event(instance_id, event))
