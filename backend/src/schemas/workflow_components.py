"""
Schemas for Workflow Components
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from enum import Enum


class ComponentCategory(str, Enum):
    TRIGGERS = "triggers"
    DATA_SOURCES = "data_sources"
    AI_PROCESSING = "ai_processing"
    CONTROL_FLOW = "control_flow"
    OUTPUT_ACTIONS = "output_actions"


class ParameterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    TEXTAREA = "textarea"
    FILE = "file"
    JSON = "json"


class ComponentParameter(BaseModel):
    name: str
    label: str
    type: ParameterType
    required: bool = False
    default_value: Optional[Any] = None
    description: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None  # For select type
    validation: Optional[Dict[str, Any]] = None


class ComponentHandle(BaseModel):
    id: str
    type: str  # "source" or "target"
    position: str  # "top", "bottom", "left", "right"
    label: Optional[str] = None


class WorkflowComponentMetadata(BaseModel):
    type: str
    name: str
    description: str
    category: ComponentCategory
    icon: str
    color: str
    parameters: List[ComponentParameter]
    input_handles: List[ComponentHandle]
    output_handles: List[ComponentHandle]
    is_trigger: bool = False
    is_async: bool = False
    max_runtime_seconds: Optional[int] = None


class ExecutionContext(BaseModel):
    workflow_id: str
    instance_id: str
    step_id: str
    input_data: Dict[str, Any]
    previous_outputs: Dict[str, Any]
    global_variables: Dict[str, Any]


class ExecutionResult(BaseModel):
    success: bool
    output_data: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    logs: List[str] = []
    next_steps: List[str] = []
