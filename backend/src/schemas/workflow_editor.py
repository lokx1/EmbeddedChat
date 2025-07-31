"""
Schemas for Workflow Editor
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class NodePosition(BaseModel):
    x: float
    y: float


class NodeData(BaseModel):
    label: str
    type: str
    config: Optional[Dict[str, Any]] = None


class WorkflowNode(BaseModel):
    id: str
    type: str
    position: NodePosition
    data: NodeData


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class WorkflowEditorData(BaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    viewport: Optional[Dict[str, Any]] = None


class SaveWorkflowRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "custom"
    workflow_data: WorkflowEditorData
    is_public: bool = False


class UpdateWorkflowRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    workflow_data: Optional[WorkflowEditorData] = None
    is_public: Optional[bool] = None


class WorkflowEditorResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    workflow_data: WorkflowEditorData
    is_public: bool
    created_at: datetime
    updated_at: datetime
