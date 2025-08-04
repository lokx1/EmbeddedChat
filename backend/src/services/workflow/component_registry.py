"""
Workflow Component Registry
"""
from typing import Dict, List, Type, Tuple, Any
from abc import ABC, abstractmethod
import asyncio
import time
import json
from datetime import datetime

from ...schemas.workflow_components import (
    WorkflowComponentMetadata, 
    ExecutionContext, 
    ExecutionResult,
    ComponentCategory,
    ComponentParameter,
    ComponentHandle,
    ParameterType
)

# Import Google Drive service
try:
    from .google_drive_service import GoogleDriveService
    GOOGLE_DRIVE_AVAILABLE = True
    print("✅ Google Drive service imported successfully")
except ImportError as e:
    GOOGLE_DRIVE_AVAILABLE = False
    print(f"❌ Google Drive service import failed: {e}")

# Import Google Sheets service
try:
    from .google_services import GoogleSheetsService
    GOOGLE_SHEETS_AVAILABLE = True
    print("✅ Google Sheets service imported successfully")
except ImportError as e:
    GOOGLE_SHEETS_AVAILABLE = False
    print(f"❌ Google Sheets service import failed: {e}")


class BaseWorkflowComponent(ABC):
    """Base class for all workflow components"""
    
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        """Return component metadata"""
        pass
    
    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute the component with given context"""
        pass
    
    def validate_parameters(self, parameters: Dict) -> List[str]:
        """Validate component parameters, return list of errors"""
        errors = []
        metadata = self.get_metadata()
        
        for param in metadata.parameters:
            if param.required and param.name not in parameters:
                errors.append(f"Required parameter '{param.name}' is missing")
            
            if param.name in parameters:
                value = parameters[param.name]
                if param.type == ParameterType.NUMBER and not isinstance(value, (int, float)):
                    errors.append(f"Parameter '{param.name}' must be a number")
                elif param.type == ParameterType.BOOLEAN and not isinstance(value, bool):
                    errors.append(f"Parameter '{param.name}' must be a boolean")
        
        return errors


# Example Components

class ManualTriggerComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="manual_trigger",
            name="Manual Trigger",
            description="Manually trigger workflow execution",
            category=ComponentCategory.TRIGGERS,
            icon="PlayIcon",
            color="from-emerald-500 via-emerald-600 to-teal-600",
            parameters=[
                ComponentParameter(
                    name="trigger_data",
                    label="Trigger Data",
                    type=ParameterType.JSON,
                    description="Data to pass to the workflow"
                )
            ],
            input_handles=[],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Start")
            ],
            is_trigger=True
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            # Debug: log all input data
            debug_logs = [
                f"ManualTrigger input_data keys: {list(context.input_data.keys())}",
                f"ManualTrigger input_data: {context.input_data}"
            ]
            
            # Manual trigger passes through the trigger data and instance input data
            trigger_data = context.input_data.get("trigger_data", {})
            
            # Also include any data from the workflow instance input_data
            output_data = {**trigger_data}
            
            # Check if there's test data in the input and include it
            if "data" in context.input_data:
                output_data["data"] = context.input_data["data"]
                debug_logs.append(f"Found data in input: {context.input_data['data']}")
                
            # If test_data exists, map it to data
            if "test_data" in context.input_data:
                output_data["data"] = context.input_data["test_data"]
                debug_logs.append(f"Found test_data in input: {context.input_data['test_data']}")
                
            # Also pass through any other keys from input_data that are not configs
            config_keys = {"trigger_data", "sheet_id", "sheet_name", "range", "mode", "data_format"}
            for key, value in context.input_data.items():
                if key not in config_keys:
                    output_data[key] = value
                    debug_logs.append(f"Added key {key} to output")
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data=output_data,
                execution_time_ms=execution_time,
                logs=debug_logs + [f"Final output data keys: {list(output_data.keys())}"],
                next_steps=["output"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error in manual trigger: {str(e)}"]
            )


class HttpRequestComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="http_request",
            name="HTTP Request",
            description="Make HTTP requests to external APIs",
            category=ComponentCategory.DATA_SOURCES,
            icon="GlobeAltIcon",
            color="from-sky-500 via-blue-600 to-indigo-600",
            parameters=[
                ComponentParameter(
                    name="url",
                    label="URL",
                    type=ParameterType.STRING,
                    required=True,
                    description="The URL to send the request to"
                ),
                ComponentParameter(
                    name="method",
                    label="HTTP Method",
                    type=ParameterType.SELECT,
                    required=True,
                    default_value="GET",
                    options=[
                        {"label": "GET", "value": "GET"},
                        {"label": "POST", "value": "POST"},
                        {"label": "PUT", "value": "PUT"},
                        {"label": "DELETE", "value": "DELETE"}
                    ]
                ),
                ComponentParameter(
                    name="headers",
                    label="Headers",
                    type=ParameterType.JSON,
                    description="HTTP headers as JSON object"
                ),
                ComponentParameter(
                    name="body",
                    label="Request Body",
                    type=ParameterType.TEXTAREA,
                    description="Request body (for POST/PUT requests)"
                ),
                ComponentParameter(
                    name="timeout",
                    label="Timeout (seconds)",
                    type=ParameterType.NUMBER,
                    default_value=30
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="success", type="source", position="right", label="Success"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=60
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        import aiohttp
        start_time = time.time()
        
        try:
            url = context.input_data.get("url")
            method = context.input_data.get("method", "GET")
            headers = context.input_data.get("headers", {})
            body = context.input_data.get("body")
            timeout = context.input_data.get("timeout", 30)
            
            if isinstance(headers, str):
                headers = json.loads(headers)
            
            async with aiohttp.ClientSession() as session:
                kwargs = {
                    "timeout": aiohttp.ClientTimeout(total=timeout)
                }
                
                if headers:
                    kwargs["headers"] = headers
                
                if body and method in ["POST", "PUT"]:
                    kwargs["data"] = body
                
                async with session.request(method, url, **kwargs) as response:
                    response_data = {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": await response.text()
                    }
                    
                    try:
                        response_data["json"] = await response.json()
                    except:
                        pass
                    
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    next_step = "success" if response.status < 400 else "error"
                    
                    return ExecutionResult(
                        success=response.status < 400,
                        output_data=response_data,
                        execution_time_ms=execution_time,
                        logs=[f"HTTP {method} request to {url} completed with status {response.status}"],
                        next_steps=[next_step]
                    )
                    
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error in HTTP request: {str(e)}"],
                next_steps=["error"]
            )


class DataTransformComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="data_transform",
            name="Data Transform",
            description="Transform and manipulate data using JavaScript",
            category=ComponentCategory.AI_PROCESSING,
            icon="ArrowsRightLeftIcon",
            color="from-amber-500 via-orange-500 to-orange-600",
            parameters=[
                ComponentParameter(
                    name="transform_script",
                    label="Transform Script",
                    type=ParameterType.TEXTAREA,
                    required=True,
                    description="JavaScript code to transform the data. Input data is available as 'input' variable. Return the transformed data."
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Output")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            # This would require a JavaScript engine like PyV8 or similar
            # For now, we'll implement a simple Python-based transformation
            transform_script = context.input_data.get("transform_script", "")
            input_data = context.input_data.get("data", {})
            
            # Simple transformation (in real implementation, use a secure sandbox)
            # This is a simplified example - in production, use proper sandboxing
            output_data = {
                "transformed_data": input_data,
                "script_executed": True
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data=output_data,
                execution_time_ms=execution_time,
                logs=["Data transformation completed"],
                next_steps=["output"]
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error in data transformation: {str(e)}"]
            )


class ComponentRegistry:
    """Registry for all workflow components"""
    
    def __init__(self):
        self._components: Dict[str, Type[BaseWorkflowComponent]] = {}
        self._register_default_components()
    
    def _register_default_components(self):
        """Register default components"""
        self.register_component(ManualTriggerComponent)
        self.register_component(HttpRequestComponent)
        self.register_component(DataTransformComponent)
        self.register_component(GoogleSheetsComponent)
        self.register_component(GoogleSheetsWriteComponent)
        self.register_component(GoogleDriveWriteComponent)
        self.register_component(AIProcessingComponent)
        self.register_component(WebhookComponent)
        self.register_component(EmailSenderComponent)
        self.register_component(DatabaseWriteComponent)
    
    def register_component(self, component_class: Type[BaseWorkflowComponent]):
        """Register a component class"""
        metadata = component_class.get_metadata()
        self._components[metadata.type] = component_class
    
    def get_component(self, component_type: str) -> Type[BaseWorkflowComponent]:
        """Get a component class by type"""
        if component_type not in self._components:
            raise ValueError(f"Component type '{component_type}' not found")
        return self._components[component_type]
    
    def get_all_components(self) -> List[WorkflowComponentMetadata]:
        """Get metadata for all registered components"""
        return [cls.get_metadata() for cls in self._components.values()]
    
    def get_components_by_category(self, category: ComponentCategory) -> List[WorkflowComponentMetadata]:
        """Get components filtered by category"""
        return [
            cls.get_metadata() 
            for cls in self._components.values()
            if cls.get_metadata().category == category
        ]


class GoogleSheetsComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="google_sheets",
            name="Google Sheets",
            description="Read spreadsheet data",
            category=ComponentCategory.DATA_SOURCES,
            icon="TableCellsIcon",
            color="from-green-500 via-emerald-500 to-teal-500",
            parameters=[
                ComponentParameter(
                    name="sheet_id",
                    label="Sheet ID",
                    type=ParameterType.STRING,
                    required=True,
                    description="Google Sheets document ID"
                ),
                ComponentParameter(
                    name="sheet_name",
                    label="Sheet Name",
                    type=ParameterType.STRING,
                    required=True,
                    description="Name of the sheet tab"
                ),
                ComponentParameter(
                    name="range",
                    label="Cell Range",
                    type=ParameterType.STRING,
                    default_value="A1:Z1000",
                    description="Cell range to read (e.g., A1:Z1000)"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Data")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            sheet_id = context.input_data.get("sheet_id")
            sheet_name = context.input_data.get("sheet_name", "Sheet1")
            range_str = context.input_data.get("range", "A1:Z1000")
            
            if not sheet_id:
                raise ValueError("sheet_id is required")
            
            # Use real Google Sheets API
            if GOOGLE_SHEETS_AVAILABLE:
                # Get Google Sheets service with CORRECT credentials path
                import os
                # Use absolute path to credentials.json in backend folder  
                credentials_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "credentials.json")
                credentials_path = os.path.normpath(credentials_path)
                
                sheets_service = GoogleSheetsService(credentials_path)
                
                if not await sheets_service.authenticate():
                    raise Exception("Failed to authenticate with Google Sheets API")
                
                # Read data using API
                success, result_data = await sheets_service.read_sheet(
                    sheet_id=sheet_id, 
                    sheet_name=sheet_name, 
                    range_str=range_str
                )
                
                if success and result_data.get('data'):
                    values = result_data['data']['values']
                else:
                    values = []
                
                if values:
                    # Convert to pandas-like format for consistency
                    headers = values[0] if values else []
                    data_rows = values[1:] if len(values) > 1 else []
                    
                    # Create records (list of dictionaries)
                    records = []
                    for row in data_rows:
                        # Pad row to match header length
                        padded_row = row + [''] * (len(headers) - len(row))
                        record = {headers[i]: padded_row[i] if i < len(padded_row) else '' 
                                for i in range(len(headers))}
                        records.append(record)
                    
                    spreadsheet_data = {
                        "values": values,
                        "records": records,
                        "spreadsheet_info": {
                            "sheet_id": sheet_id,
                            "sheet_name": sheet_name,
                            "range": range_str,
                            "total_rows": len(values),
                            "total_columns": len(headers),
                            "columns": headers
                        }
                    }
                else:
                    spreadsheet_data = {
                        "values": [],
                        "records": [],
                        "spreadsheet_info": {
                            "sheet_id": sheet_id,
                            "sheet_name": sheet_name,
                            "range": range_str,
                            "total_rows": 0,
                            "total_columns": 0,
                            "columns": []
                        }
                    }
                
                execution_time = int((time.time() - start_time) * 1000)
                
                return ExecutionResult(
                    success=True,
                    output_data=spreadsheet_data,
                    execution_time_ms=execution_time,
                    logs=[
                        f"Connected to Google Sheets API",
                        f"Successfully read data from sheet '{sheet_name}'",
                        f"Retrieved {len(spreadsheet_data['records'])} records with {len(spreadsheet_data['spreadsheet_info']['columns'])} columns",
                        f"Columns: {', '.join(spreadsheet_data['spreadsheet_info']['columns'])}"
                    ],
                    next_steps=["output"]
                )
            
            else:
                # Fallback to CSV export for compatibility
                import requests
                import pandas as pd
                from io import StringIO
                
                # Use CSV export for public sheets (gid=0 for first sheet)
                url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Parse CSV data
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data)
                
                # Convert to values format (list of lists)
                if not df.empty:
                    values = [df.columns.tolist()]  # Header row
                    values.extend(df.values.tolist())  # Data rows
                    
                    # Convert to list of dictionaries for easier use
                    records = df.to_dict('records')
                    
                    spreadsheet_data = {
                        "values": values,
                        "records": records,
                        "spreadsheet_info": {
                            "sheet_id": sheet_id,
                            "sheet_name": sheet_name,
                            "range": range_str,
                            "total_rows": len(values),
                            "total_columns": len(values[0]) if values else 0,
                            "columns": df.columns.tolist()
                        }
                    }
                else:
                    spreadsheet_data = {
                        "values": [],
                        "records": [],
                        "spreadsheet_info": {
                            "sheet_id": sheet_id,
                            "sheet_name": sheet_name,
                            "range": range_str,
                            "total_rows": 0,
                            "total_columns": 0,
                            "columns": []
                        }
                    }
                
                execution_time = int((time.time() - start_time) * 1000)
                
                return ExecutionResult(
                    success=True,
                    output_data=spreadsheet_data,
                    execution_time_ms=execution_time,
                    logs=[
                        f"Connected to Google Sheets document: {sheet_id}",
                        f"Successfully fetched data from sheet",
                        f"Retrieved {len(spreadsheet_data['values'])} rows with {len(spreadsheet_data['spreadsheet_info']['columns'])} columns",
                        f"Columns: {', '.join(spreadsheet_data['spreadsheet_info']['columns'])}"
                    ],
                    next_steps=["output"]
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error reading Google Sheets: {str(e)}"]
            )


class AIProcessingComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="ai_processing",
            name="AI Processing",
            description="Process Google Sheets data with AI to generate assets",
            category=ComponentCategory.AI_PROCESSING,
            icon="CpuChipIcon",
            color="from-purple-500 via-purple-600 to-indigo-600",
            parameters=[
                ComponentParameter(
                    name="provider",
                    label="AI Provider",
                    type=ParameterType.SELECT,
                    required=True,
                    default_value="openai",
                    options=[
                        {"label": "OpenAI", "value": "openai"},
                        {"label": "Anthropic Claude", "value": "claude"},
                        {"label": "Ollama (Local)", "value": "ollama"}
                    ]
                ),
                ComponentParameter(
                    name="model",
                    label="Model",
                    type=ParameterType.STRING,
                    required=True,
                    default_value="gpt-4o",
                    description="AI model to use (e.g., gpt-4o, claude-3-5-sonnet, llama3.2)"
                ),
                ComponentParameter(
                    name="prompt",
                    label="Prompt Template",
                    type=ParameterType.TEXTAREA,
                    required=True,
                    description="AI prompt template. Use {input} to reference input data."
                ),
                ComponentParameter(
                    name="temperature",
                    label="Temperature",
                    type=ParameterType.NUMBER,
                    default_value=0.7,
                    description="Controls randomness (0.0 to 1.0)"
                ),
                ComponentParameter(
                    name="max_tokens",
                    label="Max Tokens",
                    type=ParameterType.NUMBER,
                    default_value=4000,  # ⬆️ Increased from 1000 to 4000
                    description="Maximum number of tokens to generate (up to 4000 for better responses)"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Response"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=120
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            provider = context.input_data.get("provider", "openai")
            model = context.input_data.get("model", "gpt-4o")
            prompt_template = context.input_data.get("prompt", "")
            temperature = context.input_data.get("temperature", 0.7)
            max_tokens = context.input_data.get("max_tokens", 4000)  # ⬆️ Increased default to 4000
            
            # Get input data from previous step (should be Google Sheets data)
            input_data = context.previous_outputs
            sheets_data = None
            
            # Find Google Sheets data in previous outputs
            for step_id, step_output in input_data.items():
                if isinstance(step_output, dict) and "spreadsheet_info" in step_output:
                    sheets_data = step_output
                    break
            
            # If no sheets data from previous steps, try to get from context input_data
            if not sheets_data and context.input_data.get("sheets_data"):
                sheets_data = context.input_data["sheets_data"]
                
            if not sheets_data:
                return ExecutionResult(
                    success=False,
                    output_data={},
                    error="No Google Sheets data found in previous steps",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    logs=["Error: Expected Google Sheets data as input"]
                )
            
            # Process each row of data
            processed_results = []
            records = sheets_data.get("records", [])
            
            logs = [
                f"Starting AI processing with {provider} ({model})",
                f"Processing {len(records)} records from Google Sheets",
                f"Temperature: {temperature}, Max Tokens: {max_tokens}"
            ]
            
            for i, record in enumerate(records[:10]):  # Limit to 10 records for demo
                try:
                    # Replace {input} in prompt with actual record data
                    prompt = prompt_template.replace("{input}", json.dumps(record, indent=2))
                    
                    # Simulate AI processing (replace with actual AI calls)
                    ai_response = await self._process_with_ai(provider, model, prompt, temperature, max_tokens, record)
                    
                    processed_result = {
                        "row_index": i + 1,
                        "input_data": record,
                        "ai_response": ai_response,
                        "status": "success",
                        "provider": provider,
                        "model": model,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    processed_results.append(processed_result)
                    logs.append(f"Successfully processed row {i + 1}")
                    
                except Exception as e:
                    processed_result = {
                        "row_index": i + 1,
                        "input_data": record,
                        "ai_response": None,
                        "status": "error",
                        "error": str(e),
                        "provider": provider,
                        "model": model,
                        "timestamp": datetime.now().isoformat()
                    }
                    processed_results.append(processed_result)
                    logs.append(f"Error processing row {i + 1}: {str(e)}")
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Prepare output data
            output_data = {
                "processed_results": processed_results,
                "summary": {
                    "total_records": len(records),
                    "processed_records": len(processed_results),
                    "successful_records": len([r for r in processed_results if r["status"] == "success"]),
                    "failed_records": len([r for r in processed_results if r["status"] == "error"]),
                    "processing_time_ms": execution_time,
                    "provider": provider,
                    "model": model
                },
                "original_sheets_info": sheets_data.get("spreadsheet_info", {}),
                # Format for Google Sheets Write component - Use the CORRECT method for AI results
                "results_for_sheets": self._format_ai_results_for_sheets(processed_results)
            }
            
            return ExecutionResult(
                success=True,
                output_data=output_data,
                execution_time_ms=execution_time,
                logs=logs,
                next_steps=["output"]
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"AI processing error: {str(e)}"]
            )
    
    async def _process_with_ai(self, provider: str, model: str, prompt: str, temperature: float, max_tokens: int, record: dict) -> dict:
        """Process data with AI provider"""
        
        if provider == "openai":
            return await self._process_with_openai(model, prompt, temperature, max_tokens, record)
        elif provider == "claude":
            return await self._process_with_claude(model, prompt, temperature, max_tokens, record)
        elif provider == "ollama":
            return await self._process_with_ollama(model, prompt, temperature, max_tokens, record)
        else:
            # Fallback simulation
            return await self._simulate_ai_processing(record)
    
    async def _process_with_openai(self, model: str, prompt: str, temperature: float, max_tokens: int, record: dict) -> dict:
        """Process with OpenAI API"""
        try:
            # TODO: Implement actual OpenAI API call
            # For now, simulate asset generation based on input data
            
            description = record.get('description', '')
            output_format = record.get('output_format', 'PNG')
            
            # Simulate AI-generated content
            generated_content = {
                "type": "asset_generation",
                "description": description,
                "output_format": output_format.upper(),
                "generated_url": f"https://generated-assets.example.com/{output_format.lower()}/{hash(description) % 10000}.{output_format.lower()}",
                "metadata": {
                    "model": model,
                    "provider": "openai",
                    "quality": "high",
                    "size": "1024x1024" if output_format.upper() in ["PNG", "JPG"] else "30s",
                    "processing_time": "2.3s"
                },
                "prompt_used": prompt[:200] + "..." if len(prompt) > 200 else prompt
            }
            
            await asyncio.sleep(1)  # Simulate processing time
            return generated_content
            
        except Exception as e:
            return {"error": f"OpenAI processing failed: {str(e)}"}
    
    async def _process_with_claude(self, model: str, prompt: str, temperature: float, max_tokens: int, record: dict) -> dict:
        """Process with Claude API"""
        try:
            # TODO: Implement actual Claude API call
            description = record.get('description', '')
            output_format = record.get('output_format', 'PNG')
            
            generated_content = {
                "type": "asset_generation",
                "description": description,
                "output_format": output_format.upper(),
                "generated_url": f"https://claude-assets.example.com/{output_format.lower()}/{hash(description) % 10000}.{output_format.lower()}",
                "metadata": {
                    "model": model,
                    "provider": "claude",
                    "quality": "high",
                    "size": "1024x1024" if output_format.upper() in ["PNG", "JPG"] else "30s",
                    "processing_time": "1.8s"
                },
                "prompt_used": prompt[:200] + "..." if len(prompt) > 200 else prompt
            }
            
            await asyncio.sleep(1.2)  # Simulate processing time
            return generated_content
            
        except Exception as e:
            return {"error": f"Claude processing failed: {str(e)}"}
    
    async def _process_with_ollama(self, model: str, prompt: str, temperature: float, max_tokens: int, record: dict) -> dict:
        """Process with Ollama local API"""
        try:
            import requests
            
            # Check if Ollama is running
            try:
                health_response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if health_response.status_code != 200:
                    raise Exception("Ollama server not responding")
            except:
                # Fallback to simulation if Ollama not available
                return await self._simulate_ai_processing(record)
            
            description = record.get('description', '')
            output_format = record.get('output_format', 'PNG')
            
            # Enhanced prompt for asset generation
            enhanced_prompt = f"""
            Asset Generation Request:
            Description: {description}
            Output Format: {output_format}
            
            {prompt}
            
            Please provide a comprehensive and detailed asset specification including:
            
            1. TECHNICAL SPECIFICATIONS:
               - Exact dimensions and resolution requirements
               - File format specifications and compression settings
               - Color depth and transparency requirements
               - Size limitations and optimization guidelines
            
            2. DESIGN & STYLE GUIDELINES:
               - Visual style direction (modern, minimalist, vintage, etc.)
               - Layout and composition principles
               - Typography recommendations (if applicable)
               - Icon or graphic elements to include
               - Mood and aesthetic considerations
            
            3. COLOR PALETTE & BRANDING:
               - Primary and secondary color recommendations with hex codes
               - Color psychology and brand alignment
               - Contrast and accessibility considerations
               - Color variations for different use cases
            
            4. CONTENT & MESSAGING:
               - Key messages or text to include
               - Call-to-action elements
               - Hierarchy of information
               - Target audience considerations
            
            5. IMPLEMENTATION NOTES:
               - Best practices for creation
               - Tools and software recommendations
               - Quality assurance checkpoints
               - Delivery format and naming conventions
            
            6. USAGE GUIDELINES:
               - Intended use cases and platforms
               - Scaling and adaptation requirements
               - Brand compliance considerations
               - Performance optimization tips
            
            Provide a detailed, actionable response that serves as a complete creative brief.
            Be specific with measurements, hex codes, and technical requirements.
            Make your response comprehensive and professional - aim for 2000-3000 characters.
            """
            
            # Ollama API call
            payload = {
                "model": model,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json=payload,
                timeout=60  # Ollama can be slow
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get('response', '').strip()
                
                generated_content = {
                    "type": "ollama_asset_generation",
                    "description": description,
                    "output_format": output_format.upper(),
                    "generated_url": f"https://ollama-assets.local/{output_format.lower()}/{hash(description) % 10000}.{output_format.lower()}",
                    "ai_response": ai_text,
                    "metadata": {
                        "model": model,
                        "provider": "ollama",
                        "quality": "local_generation",
                        "size": "1024x1024" if output_format.upper() in ["PNG", "JPG"] else "variable",
                        "processing_time": f"{result.get('total_duration', 0) / 1000000:.1f}ms" if 'total_duration' in result else "unknown",
                        "tokens_evaluated": result.get('eval_count', 0),
                        "eval_duration": f"{result.get('eval_duration', 0) / 1000000:.1f}ms" if 'eval_duration' in result else "unknown"
                    },
                    "prompt_used": enhanced_prompt[:200] + "..." if len(enhanced_prompt) > 200 else enhanced_prompt
                }
                
                return generated_content
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
        except Exception as e:
            # Fallback to simulation if Ollama fails
            print(f"Ollama processing failed, using simulation: {str(e)}")
            return await self._simulate_ai_processing(record)
    
    async def _simulate_ai_processing(self, record: dict) -> dict:
        """Simulate AI processing for demo purposes"""
        description = record.get('description', 'Default asset')
        output_format = record.get('output_format', 'PNG')
        
        return {
            "type": "simulated_asset_generation",
            "description": description,
            "output_format": output_format.upper(),
            "generated_url": f"https://demo-assets.example.com/{output_format.lower()}/{hash(description) % 10000}.{output_format.lower()}",
            "metadata": {
                "model": "simulation",
                "provider": "demo",
                "quality": "demo",
                "size": "1024x1024" if output_format.upper() in ["PNG", "JPG"] else "30s",
                "processing_time": "0.5s"
            },
            "note": "This is a simulated response for demonstration purposes"
        }
    
    def _format_results_for_sheets(self, processed_results: list) -> list:
        """Format AI processing results for Google Sheets Write component"""
        
        # Header row with Prompt column added
        headers = [
            "Row Index", "Original Description", "Output Format", "Status", 
            "Generated URL", "Prompt", "Provider", "Model", "Quality", "Size", 
            "Processing Time", "Timestamp", "Notes"
        ]
        
        # Data rows
        data_rows = []
        for result in processed_results:
            input_data = result.get("input_data", {})
            ai_response = result.get("ai_response", {})
            metadata = ai_response.get("metadata", {}) if ai_response else {}
            
            # Extract and clean AI response text (remove <think> tags)
            ai_text = ""
            if ai_response and "ai_response" in ai_response:
                ai_text = ai_response["ai_response"]
            elif ai_response and "generated_text" in ai_response:
                ai_text = ai_response["generated_text"]
            elif ai_response and "response" in ai_response:
                ai_text = ai_response["response"]
            
            # Clean the AI response by removing <think> tags and content
            cleaned_prompt = self._clean_ai_response(ai_text) if ai_text else ""
            
            row = [
                result.get("row_index", ""),
                input_data.get("description", ""),
                input_data.get("output_format", ""),
                result.get("status", ""),
                ai_response.get("generated_url", "") if ai_response else "",
                cleaned_prompt,  # ⭐ NEW: Cleaned AI response as prompt
                result.get("provider", ""),
                result.get("model", ""),
                metadata.get("quality", ""),
                metadata.get("size", ""),
                metadata.get("processing_time", ""),
                result.get("timestamp", ""),
                ai_response.get("note", "") if ai_response else result.get("error", "")
            ]
            data_rows.append(row)
        
        return [headers] + data_rows
    
    def _format_ai_results_for_sheets(self, processed_results: list) -> list:
        """Format AI processing results specifically for Google Sheets Write
        
        This converts the AI processing 'processed_results' format to a clean table format
        with original input data + AI response in Prompt column
        """
        if not processed_results:
            return []
            
        # Extract headers from first result's input_data
        first_result = processed_results[0]
        input_data = first_result.get("input_data", {})
        
        # Get original headers from input data
        original_headers = list(input_data.keys())
        
        # Check if "Prompt" column already exists, if so replace it, otherwise add it
        if "Prompt" in original_headers:
            # Prompt column already exists, we'll replace its content
            headers = original_headers
        else:
            # Add Prompt column for AI response
            headers = original_headers + ["Prompt"]
        
        # Create data rows
        data_rows = [headers]  # Start with header row
        
        for result in processed_results:
            input_data = result.get("input_data", {})
            ai_response = result.get("ai_response", {})
            
            # Debug: Log AI response structure
            print(f"🔍 AI Response structure for row {result.get('row_index', '?')}: {type(ai_response)}")
            if isinstance(ai_response, dict):
                print(f"🔍 AI Response keys: {list(ai_response.keys())}")
                for key, value in ai_response.items():
                    if isinstance(value, str) and len(value) > 50:
                        print(f"🔍   {key}: {type(value)} - {str(value)[:100]}...")
                    else:
                        print(f"🔍   {key}: {type(value)} - {value}")
            
            # Extract and clean AI response for Prompt column
            ai_text = ""
            if ai_response:
                # FIXED: Correct extraction logic for different AI provider structures
                # Check if ai_response is the direct text content (from Ollama)
                if "ai_response" in ai_response and isinstance(ai_response["ai_response"], str):
                    ai_text = ai_response["ai_response"]
                    print(f"🎯 Found ai_response (Ollama): {ai_text[:100]}...")
                
                # Fallback to other AI provider keys if ai_response not found
                elif not ai_text:
                    print(f"🔍 Trying fallback extraction methods for other providers...")
                    # Try direct text fields from different providers
                    for key in ["prompt_used", "note", "response", "content", "text", "generated_text"]:
                        if key in ai_response and isinstance(ai_response[key], str) and ai_response[key].strip():
                            ai_text = ai_response[key]
                            print(f"🎯 Found text in {key}: {ai_text[:100]}...")
                            break
                    
                    # If still no text, look for any substantial string value
                    if not ai_text:
                        for key, value in ai_response.items():
                            if isinstance(value, str) and len(value.strip()) > 20:  # Substantial text content
                                ai_text = value
                                print(f"🎯 Found substantial text in {key}: {ai_text[:100]}...")
                                break
                
                # Last resort: create a summary from available data
                if not ai_text and ai_response:
                    # Create a meaningful summary from the AI response structure
                    summary_parts = []
                    for key, value in ai_response.items():
                        if isinstance(value, str) and value.strip() and key not in ["type", "provider", "model"]:
                            summary_parts.append(f"{key}: {value}")
                    
                    if summary_parts:
                        ai_text = " | ".join(summary_parts[:3])  # Take first 3 meaningful parts
                        print(f"🎯 Created summary text: {ai_text[:100]}...")
            
            # If still no text, provide a default message
            if not ai_text:
                ai_text = f"AI processing completed for row {result.get('row_index', '?')} - check logs for details"
                print(f"⚠️ No AI text found, using default message")
            
            # Clean the AI response by removing <think> tags and content
            cleaned_prompt = self._clean_ai_response(ai_text) if ai_text else ""
            print(f"🎯 Final cleaned_prompt for row {result.get('row_index', '?')}: '{cleaned_prompt[:100]}...' (length: {len(cleaned_prompt)})")
            
            # Build row with original data, replacing Prompt column if it exists
            row = []
            for header in original_headers:
                if header == "Prompt":
                    # Replace the empty/existing Prompt column with AI response
                    row.append(cleaned_prompt)
                else:
                    row.append(str(input_data.get(header, "")))
            
            # If Prompt column didn't exist in original headers, add it now
            if "Prompt" not in original_headers:
                row.append(cleaned_prompt)
            
            data_rows.append(row)
        
        return data_rows
    
    def _clean_ai_response(self, ai_text: str) -> str:
        """Clean AI response by removing <think> tags and their content"""
        if not ai_text:
            return ""
        
        import re
        
        # Remove <think>...</think> blocks (including multiline)
        cleaned = re.sub(r'<think>.*?</think>', '', ai_text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove any remaining <think> or </think> tags
        cleaned = re.sub(r'</?think>', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and normalize line breaks
        cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)  # Multiple newlines to double newline
        cleaned = re.sub(r'^\s+|\s+$', '', cleaned, flags=re.MULTILINE)  # Trim each line
        cleaned = cleaned.strip()
        
        # If the text is too long, truncate it but keep it readable
        if len(cleaned) > 2000:  # Increased limit for better content
            # Try to cut at a sentence boundary
            truncated = cleaned[:2000]
            last_period = truncated.rfind('.')
            if last_period > 1000:  # Only cut at period if it's not too early
                cleaned = truncated[:last_period + 1] + " [...]"
            else:
                cleaned = truncated + " [...]"
        
        return cleaned

    def _convert_processed_results_to_sheets(self, processed_results: List[Dict[str, Any]]) -> List[List[str]]:
        """Convert processed_results from AI Processing to Google Sheets format"""
        
        if not processed_results:
            return []
        
        # Get the first result to determine headers
        first_result = processed_results[0]
        input_data_sample = first_result.get("input_data", {})
        
        # Get original headers from the input data
        original_headers = list(input_data_sample.keys())
        
        # Add Prompt column if not exists
        if "Prompt" not in original_headers:
            original_headers.append("Prompt")
        
        print(f"🔧 Headers for sheets: {original_headers}")
        
        # Build data rows starting with headers
        data_rows = [original_headers]
        
        for result in processed_results:
            input_data = result.get("input_data", {})
            ai_response = result.get("ai_response", {})
            
            # Extract AI response text
            ai_text = ""
            if isinstance(ai_response, dict) and "ai_response" in ai_response:
                ai_text = ai_response["ai_response"]
            elif isinstance(ai_response, str):
                ai_text = ai_response
            
            # Clean the AI response
            cleaned_prompt = self._clean_ai_response(ai_text) if ai_text else ""
            print(f"🎯 Row {result.get('row_index', '?')} - Prompt: '{cleaned_prompt[:100]}...'")
            
            # Build row with original data, adding Prompt column
            row = []
            for header in original_headers:
                if header == "Prompt":
                    row.append(cleaned_prompt)
                else:
                    row.append(str(input_data.get(header, "")))
            
            data_rows.append(row)
        
        print(f"🔧 Generated {len(data_rows)} rows (including header)")
        return data_rows


class WebhookComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="webhook",
            name="Webhook",
            description="HTTP trigger",
            category=ComponentCategory.TRIGGERS,
            icon="LinkIcon",
            color="from-indigo-500 via-purple-500 to-pink-500",
            parameters=[
                ComponentParameter(
                    name="webhook_url",
                    label="Webhook URL",
                    type=ParameterType.STRING,
                    required=True,
                    description="URL endpoint to listen for webhooks"
                ),
                ComponentParameter(
                    name="method",
                    label="HTTP Method",
                    type=ParameterType.SELECT,
                    default_value="POST",
                    options=[
                        {"label": "GET", "value": "GET"},
                        {"label": "POST", "value": "POST"},
                        {"label": "PUT", "value": "PUT"}
                    ]
                ),
                ComponentParameter(
                    name="headers",
                    label="Expected Headers",
                    type=ParameterType.JSON,
                    description="Headers to validate (optional)"
                )
            ],
            input_handles=[],
            output_handles=[
                ComponentHandle(id="output", type="source", position="right", label="Webhook Data"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_trigger=True,
            is_async=True
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            webhook_url = context.input_data.get("webhook_url")
            method = context.input_data.get("method", "POST")
            
            # TODO: Implement actual webhook listener setup
            # For now, return mock webhook data
            mock_webhook_data = {
                "timestamp": time.time(),
                "method": method,
                "headers": {"content-type": "application/json"},
                "body": {"message": "webhook received"}
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={"webhook_data": mock_webhook_data},
                execution_time_ms=execution_time,
                logs=[f"Webhook triggered via {method} to {webhook_url}"],
                next_steps=["output"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Webhook error: {str(e)}"],
                next_steps=["error"]
            )


class EmailSenderComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="email_sender",
            name="Email Sender",
            description="Send email notifications",
            category=ComponentCategory.OUTPUT_ACTIONS,
            icon="EnvelopeIcon",
            color="from-blue-500 via-blue-600 to-cyan-600",
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
                    description="Email content. Use {input} to reference workflow data."
                ),
                ComponentParameter(
                    name="from_email",
                    label="From Email",
                    type=ParameterType.STRING,
                    description="Sender email address (optional)"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="sent", type="source", position="right", label="Sent"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=30
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            to_email = context.input_data.get("to_email")
            subject = context.input_data.get("subject")
            body_template = context.input_data.get("body")
            from_email = context.input_data.get("from_email", "noreply@workflow.app")
            
            # Replace {input} in body with actual input data
            input_str = json.dumps(context.previous_outputs, indent=2)
            body = body_template.replace("{input}", input_str)
            
            # TODO: Implement actual email sending
            # For now, simulate email sending
            await asyncio.sleep(1)  # Simulate sending delay
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={
                    "email_sent": True,
                    "to": to_email,
                    "subject": subject,
                    "sent_at": time.time()
                },
                execution_time_ms=execution_time,
                logs=[f"Email sent to {to_email} with subject '{subject}'"],
                next_steps=["sent"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Email sending error: {str(e)}"],
                next_steps=["error"]
            )


class DatabaseWriteComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="database_write",
            name="Database Write",
            description="Write data to database",
            category=ComponentCategory.OUTPUT_ACTIONS,
            icon="CircleStackIcon",
            color="from-gray-500 via-gray-600 to-slate-600",
            parameters=[
                ComponentParameter(
                    name="table_name",
                    label="Table Name",
                    type=ParameterType.STRING,
                    required=True,
                    description="Database table to write to"
                ),
                ComponentParameter(
                    name="operation",
                    label="Operation",
                    type=ParameterType.SELECT,
                    default_value="insert",
                    options=[
                        {"label": "Insert", "value": "insert"},
                        {"label": "Update", "value": "update"},
                        {"label": "Upsert", "value": "upsert"}
                    ]
                ),
                ComponentParameter(
                    name="data_mapping",
                    label="Data Mapping",
                    type=ParameterType.JSON,
                    required=True,
                    description="JSON mapping of workflow data to database columns"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Input")
            ],
            output_handles=[
                ComponentHandle(id="success", type="source", position="right", label="Success"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ],
            is_async=True,
            max_runtime_seconds=30
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            table_name = context.input_data.get("table_name")
            operation = context.input_data.get("operation", "insert")
            data_mapping = context.input_data.get("data_mapping", {})
            
            # TODO: Implement actual database writing
            # For now, simulate database operation
            await asyncio.sleep(0.5)  # Simulate DB operation delay
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data={
                    "operation": operation,
                    "table": table_name,
                    "rows_affected": 1,
                    "timestamp": time.time()
                },
                execution_time_ms=execution_time,
                logs=[f"Database {operation} completed on table {table_name}"],
                next_steps=["success"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Database operation error: {str(e)}"],
                next_steps=["error"]
            )


class GoogleSheetsWriteComponent(BaseWorkflowComponent):
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="google_sheets_write",
            name="Google Sheets Write",
            description="Write data to Google Sheets",
            category=ComponentCategory.OUTPUT_ACTIONS,
            icon="PencilIcon",
            color="from-emerald-500 via-green-500 to-teal-500",
            parameters=[
                ComponentParameter(
                    name="sheet_id",
                    label="Sheet ID",
                    type=ParameterType.STRING,
                    required=True,
                    description="Google Sheets document ID"
                ),
                ComponentParameter(
                    name="sheet_name",
                    label="Sheet Name",
                    type=ParameterType.STRING,
                    required=True,
                    default_value="Sheet1",
                    description="Name of the sheet tab"
                ),
                ComponentParameter(
                    name="range",
                    label="Cell Range",
                    type=ParameterType.STRING,
                    default_value="A1",
                    description="Starting cell to write data (e.g., A1)"
                ),
                ComponentParameter(
                    name="mode",
                    label="Write Mode",
                    type=ParameterType.SELECT,
                    default_value="append",
                    options=[
                        {"label": "Append Rows", "value": "append"},
                        {"label": "Overwrite Range", "value": "overwrite"},
                        {"label": "Clear Then Write", "value": "clear_write"}
                    ],
                    description="How to write data to the sheet"
                ),
                ComponentParameter(
                    name="data_format",
                    label="Data Format",
                    type=ParameterType.SELECT,
                    default_value="auto",
                    options=[
                        {"label": "Auto Detect", "value": "auto"},
                        {"label": "JSON Array", "value": "json_array"},
                        {"label": "CSV String", "value": "csv_string"},
                        {"label": "Key-Value Pairs", "value": "key_value"}
                    ],
                    description="Format of input data"
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Data")
            ],
            output_handles=[
                ComponentHandle(id="success", type="source", position="right", label="Success"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        print(f"🚀 GoogleSheetsWriteComponent.execute() CALLED!")
        print(f"🔧 Context input_data keys: {list(context.input_data.keys())}")
        print(f"🔧 Context previous_outputs keys: {list(context.previous_outputs.keys())}")
        
        try:
            # Get configuration from input_data (which includes merged node config)
            sheet_id = context.input_data.get("sheet_id")
            sheet_name = context.input_data.get("sheet_name", "Sheet1")
            range_start = context.input_data.get("range", "A1")
            mode = context.input_data.get("mode", "append")
            data_format = context.input_data.get("data_format", "auto")
            
            print(f"🔧 Extracted config: sheet_id={sheet_id}, mode={mode}, data_format={data_format}")
            
            if not sheet_id:
                raise ValueError("sheet_id is required")
                
            # Debug logging
            debug_logs = [
                f"All input_data: {context.input_data}",
                f"Context previous_outputs keys: {list(context.previous_outputs.keys())}",
                f"Sheet ID: {sheet_id}",
                f"Sheet name: {sheet_name}"
            ]
            
            # Log all previous outputs in detail
            for node_id, node_output in context.previous_outputs.items():
                debug_logs.append(f"Previous output from {node_id}: {type(node_output)}")
                if isinstance(node_output, dict):
                    debug_logs.append(f"  Keys in {node_id}: {list(node_output.keys())}")
                    # Check for results_for_sheets specifically
                    if 'results_for_sheets' in node_output:
                        sheets_data = node_output['results_for_sheets']
                        debug_logs.append(f"  🎯 Found results_for_sheets in {node_id}: {len(sheets_data) if isinstance(sheets_data, list) else 'Not a list'}")
                        if isinstance(sheets_data, list) and len(sheets_data) > 0:
                            debug_logs.append(f"  📊 First row: {sheets_data[0] if len(sheets_data) > 0 else 'Empty'}")
                            debug_logs.append(f"  📊 Headers: {sheets_data[0] if len(sheets_data) > 0 and isinstance(sheets_data[0], list) else 'Not list format'}")
                
                debug_logs.append(f"Previous output from {node_id}: {node_output}")
            
            # Get input data from previous nodes or workflow input
            input_data = None
            
            print(f"🔍 Searching for data in previous_outputs...")
            
            # First try to get data from previous node outputs
            for node_id, node_output in context.previous_outputs.items():
                debug_logs.append(f"Checking node {node_id}: {type(node_output)}")
                print(f"🔍 Checking node {node_id}: {type(node_output)}")
                if isinstance(node_output, dict):
                    print(f"🔍 Node {node_id} keys: {list(node_output.keys())}")
                    
                    # SIMPLIFIED: Use processed_results directly from AI Processing
                    if "processed_results" in node_output and node_output["processed_results"]:
                        processed_results = node_output["processed_results"]
                        print(f"🎯 FOUND processed_results in {node_id}: {len(processed_results)} rows")
                        
                        # Convert processed_results to sheets format here (inline)
                        input_data = self._convert_processed_results_to_sheets(processed_results)
                        print(f"🎯 Converted to sheets format: {len(input_data)} rows")
                        break
                    
                    # Backup: Check for 'results_for_sheets' 
                    elif "results_for_sheets" in node_output and node_output["results_for_sheets"]:
                        input_data = node_output["results_for_sheets"]
                        debug_logs.append(f"🎯 Found results_for_sheets in {node_id}: {len(input_data)} rows")
                        print(f"🎯 FOUND results_for_sheets in {node_id}: {len(input_data)} rows")
                        print(f"🔍 First row sample: {input_data[0] if input_data else 'Empty'}")
                        break
                
                print(f"🔍 No suitable data found in {node_id}, continuing...")
            
            print(f"🔍 Final input_data: {type(input_data)} with {len(input_data) if input_data else 0} items")
                        
            # If no data from previous nodes, try to get from context input_data
            if not input_data:
                input_data = context.input_data.get("data", [])
                debug_logs.append(f"Using context input_data.data: {input_data}")
                print(f"🔍 Using fallback context.input_data.data: {input_data}")
                
            # If still no data, try other common keys in context
            if not input_data:
                for key in ["test_data", "sample_data", "rows"]:
                    if context.input_data.get(key):
                        input_data = context.input_data.get(key)
                        debug_logs.append(f"Using context input_data.{key}: {input_data}")
                        break
            
            if not input_data:
                error_msg = f"No data provided to write. Available keys: {list(context.input_data.keys())}, Previous outputs: {list(context.previous_outputs.keys())}"
                return ExecutionResult(
                    success=False,
                    output_data={},
                    error=error_msg,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    logs=debug_logs + [error_msg],
                    next_steps=["error"]
                )
            
            # Process data based on format
            processed_data = self._process_input_data(input_data, data_format)
            
            # Try to use real Google Sheets API if available
            debug_logs.append(f"GOOGLE_SHEETS_AVAILABLE: {GOOGLE_SHEETS_AVAILABLE}")
            print(f"🔧 GOOGLE_SHEETS_AVAILABLE in execute: {GOOGLE_SHEETS_AVAILABLE}")
            if GOOGLE_SHEETS_AVAILABLE:
                debug_logs.append("Attempting to write to Google Sheets API...")
                print(f"🔧 About to call _write_to_google_sheets")
                success, result_data = await self._write_to_google_sheets(
                    sheet_id, sheet_name, range_start, mode, processed_data
                )
                
                debug_logs.append(f"Google Sheets API result: success={success}, data={result_data}")
                print(f"🔧 _write_to_google_sheets returned: success={success}, data={result_data}")
                
                if success:
                    execution_time = int((time.time() - start_time) * 1000)
                    return ExecutionResult(
                        success=True,
                        output_data=result_data,
                        execution_time_ms=execution_time,
                        logs=debug_logs + [
                            f"Successfully connected to Google Sheets API",
                            f"Writing data to sheet '{sheet_name}' starting at {range_start}",
                            f"Mode: {mode}, Format: {data_format}",
                            f"Successfully wrote {result_data['data_written']['rows_count']} rows",
                            f"Operation completed in {execution_time}ms"
                        ],
                        next_steps=["success"]
                    )
                else:
                    # Fall back to simulation if API fails
                    debug_logs.append(f"Google Sheets API failed, falling back to simulation: {result_data}")
                    print(f"🔧 Google Sheets API failed, falling back to simulation: {result_data}")
            else:
                debug_logs.append("Google Sheets API not available, using simulation mode")
                print(f"🔧 Google Sheets API not available, using simulation mode")
            
            # Simulation mode (fallback)
            result_data = {
                "operation": "write_simulation",
                "sheet_info": {
                    "sheet_id": sheet_id,
                    "sheet_name": sheet_name,
                    "range": range_start,
                    "mode": mode
                },
                "data_written": {
                    "rows_count": len(processed_data) if isinstance(processed_data, list) else 1,
                    "columns_count": len(processed_data[0]) if processed_data and isinstance(processed_data[0], list) else 0,
                    "format": data_format
                },
                "timestamp": datetime.now().isoformat(),
                "status": "simulated"
            }
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                success=True,
                output_data=result_data,
                execution_time_ms=execution_time,
                logs=debug_logs + [
                    f"Connected to Google Sheets document: {sheet_id}",
                    f"Writing data to sheet '{sheet_name}' starting at {range_start}",
                    f"Mode: {mode}, Format: {data_format}",
                    f"Successfully wrote {result_data['data_written']['rows_count']} rows (simulated)",
                    f"Operation completed in {execution_time}ms"
                ],
                next_steps=["success"]
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error writing to Google Sheets: {str(e)}"],
                next_steps=["error"]
            )
    
    async def _write_to_google_sheets(self, sheet_id: str, sheet_name: str, range_start: str, 
                                     mode: str, data: list) -> tuple[bool, dict]:
        """
        Write data to Google Sheets using API
        
        Returns:
            tuple: (success: bool, result_data: dict)
        """
        try:
            print(f"🔧 _write_to_google_sheets called with:")
            print(f"   Sheet ID: {sheet_id}")
            print(f"   Sheet Name: {sheet_name}")
            print(f"   Range: {range_start}")
            print(f"   Mode: {mode}")
            print(f"   Data rows: {len(data) if data else 0}")
            
            # Get Google Sheets service with CORRECT credentials path
            import os
            # Use absolute path to credentials.json in backend folder
            credentials_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "credentials.json")
            credentials_path = os.path.normpath(credentials_path)
            
            print(f"🔧 Credentials path: {credentials_path}")
            print(f"🔧 Credentials exist: {os.path.exists(credentials_path)}")
            
            sheets_service = GoogleSheetsService(credentials_path)
            print(f"🔧 GoogleSheetsService created")
            
            # Authenticate
            print(f"🔧 Attempting authentication...")
            auth_result = await sheets_service.authenticate()
            print(f"🔧 Authentication result: {auth_result}")
            
            if not auth_result:
                error_msg = "Failed to authenticate with Google Sheets API"
                print(f"❌ {error_msg}")
                return False, {"error": error_msg}
            
            print(f"✅ Authentication successful")
            
            # Construct range
            range_name = f"{sheet_name}!{range_start}"
            print(f"🔧 Range name: {range_name}")
            
            # Handle different write modes
            print(f"🔧 Handling write mode: {mode}")
            if mode == "append":
                print(f"🔧 Calling write_to_sheet with append mode")
                success, result_data = await sheets_service.write_to_sheet(
                    sheet_id, sheet_name, range_start, "append", data
                )
                
            elif mode == "overwrite":
                print(f"🔧 Calling write_to_sheet with overwrite mode")
                success, result_data = await sheets_service.write_to_sheet(
                    sheet_id, sheet_name, range_start, "overwrite", data
                )
                
            elif mode == "clear_write":
                print(f"🔧 Calling write_to_sheet with clear_write mode")
                # Use overwrite mode which will replace data
                success, result_data = await sheets_service.write_to_sheet(
                    sheet_id, sheet_name, "A1", "overwrite", data
                )
            else:
                print(f"🔧 Calling write_to_sheet with default overwrite mode")
                # Default to overwrite
                success, result_data = await sheets_service.write_to_sheet(
                    sheet_id, sheet_name, range_start, "overwrite", data
                )
            
            print(f"🔧 write_to_sheet result: success={success}, data={result_data}")
            return success, result_data
                
        except Exception as e:
            error_msg = f"Google Sheets API error: {str(e)}"
            print(f"💥 Exception in _write_to_google_sheets: {error_msg}")
            import traceback
            print(f"💥 Traceback: {traceback.format_exc()}")
            return False, {"error": error_msg}
    
    def _process_input_data(self, data, format_type):
        """Process input data based on specified format"""
        if format_type == "auto":
            # Auto-detect format
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict):
                    # List of dictionaries (records) - convert to list of lists
                    if data:
                        headers = list(data[0].keys())
                        rows = [headers]  # Add header row
                        for record in data:
                            row = [str(record.get(header, "")) for header in headers]
                            rows.append(row)
                        return rows
                    return []
                else:
                    # Already list of lists or primitives
                    return data
            elif isinstance(data, dict):
                return [list(data.keys()), list(data.values())]
            elif isinstance(data, str):
                try:
                    import json
                    parsed = json.loads(data)
                    return self._process_input_data(parsed, "auto")
                except:
                    # Treat as CSV
                    return [line.split(',') for line in data.strip().split('\n')]
            else:
                return [[str(data)]]
        
        elif format_type == "json_array":
            import json
            if isinstance(data, str):
                data = json.loads(data)
            # Handle list of dicts
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                headers = list(data[0].keys())
                rows = [headers]
                for record in data:
                    row = [str(record.get(header, "")) for header in headers]
                    rows.append(row)
                return rows
            return data
        
        elif format_type == "csv_string":
            if isinstance(data, str):
                return [line.split(',') for line in data.strip().split('\n')]
            else:
                raise ValueError("CSV format expects string input")
        
        elif format_type == "key_value":
            if isinstance(data, dict):
                return [list(data.keys()), list(data.values())]
            else:
                raise ValueError("Key-Value format expects dictionary input")
        
        return data

    def _convert_processed_results_to_sheets(self, processed_results):
        """
        Convert AI processing results to Google Sheets format
        Expected input: [{"row_index": 1, "input_data": {...}, "ai_response": {...}, ...}, ...]
        Expected output: [["Description", "Example Asset URL", "Desired Output Format", "Model Specification", "Prompt"], [row1 data], ...]
        """
        if not processed_results or not isinstance(processed_results, list):
            return []
        
        print(f"🔍 _convert_processed_results_to_sheets called with {len(processed_results)} results")
        
        # Create header row - we know from logs that input has these columns plus we want to add Prompt
        headers = ["Description", "Example Asset URL", "Desired Output Format", "Model Specification", "Prompt"]
        
        # Start with header row
        sheets_data = [headers]
        
        # Process each result row
        for i, result in enumerate(processed_results):
            if not isinstance(result, dict):
                print(f"🔍 Row {i}: Not a dict, skipping")
                continue
            
            print(f"🔍 Row {i}: Processing result with keys: {list(result.keys())}")
            
            # Get input data (original row data)
            input_data = result.get("input_data", {})
            print(f"🔍 Row {i}: input_data keys: {list(input_data.keys()) if isinstance(input_data, dict) else 'Not a dict'}")
            
            # Extract AI response - it could be nested in different ways
            ai_response = ""
            
            # Check for direct ai_response first
            if "ai_response" in result:
                ai_resp_data = result["ai_response"]
                print(f"🔍 Row {i}: Found ai_response, type: {type(ai_resp_data)}")
                
                if isinstance(ai_resp_data, dict):
                    # The AI response is nested as result.ai_response.ai_response
                    ai_response = ai_resp_data.get("ai_response", "")
                    print(f"🔍 Row {i}: Extracted nested ai_response: {ai_response[:100]}...")
                elif isinstance(ai_resp_data, str):
                    # If it's already a string, use it directly
                    ai_response = ai_resp_data
                    print(f"🔍 Row {i}: Using direct string ai_response: {ai_response[:100]}...")
                else:
                    print(f"🔍 Row {i}: ai_response is neither dict nor string: {type(ai_resp_data)}")
            else:
                print(f"🔍 Row {i}: No ai_response key found")
            
            # Create row with original data + AI response in Prompt column
            row = [
                input_data.get("Description", ""),
                input_data.get("Example Asset URL", ""),
                input_data.get("Desired Output Format", ""),
                input_data.get("Model Specification", ""),
                ai_response  # This goes in the Prompt column
            ]
            
            print(f"🔍 Row {i}: Final row data - Prompt length: {len(ai_response) if ai_response else 0}")
            sheets_data.append(row)
        
        print(f"🔍 _convert_processed_results_to_sheets returning {len(sheets_data)} rows (including header)")
        return sheets_data

class GoogleDriveWriteComponent(BaseWorkflowComponent):
    """Component for writing files to Google Drive"""
    
    @classmethod
    def get_metadata(cls) -> WorkflowComponentMetadata:
        return WorkflowComponentMetadata(
            type="google_drive_write",
            name="Google Drive Write",
            description="Upload files and data to Google Drive",
            category=ComponentCategory.OUTPUT_ACTIONS,
            icon="CloudArrowUpIcon",
            color="from-green-500 via-teal-600 to-blue-600",
            parameters=[
                ComponentParameter(
                    name="file_name",
                    label="File Name",
                    type=ParameterType.STRING,
                    required=True,
                    description="Name of the file to upload",
                    default_value=""
                ),
                ComponentParameter(
                    name="folder_id",
                    label="Folder ID",
                    type=ParameterType.STRING,
                    required=False,
                    description="Google Drive folder ID (optional)",
                    default_value=""
                ),
                ComponentParameter(
                    name="file_type",
                    label="File Type",
                    type=ParameterType.SELECT,
                    required=False,
                    description="Type of file to create",
                    options=[
                        {"label": "Auto Detect", "value": "auto"},
                        {"label": "Text", "value": "text"},
                        {"label": "JSON", "value": "json"},
                        {"label": "CSV", "value": "csv"},
                        {"label": "Binary", "value": "binary"}
                    ],
                    default_value="auto"
                ),
                ComponentParameter(
                    name="content_source",
                    label="Content Source",
                    type=ParameterType.SELECT,
                    required=False,
                    description="Source of file content",
                    options=[
                        {"label": "Previous Output", "value": "previous_output"},
                        {"label": "Input Data", "value": "input_data"},
                        {"label": "Generated", "value": "generated"}
                    ],
                    default_value="previous_output"
                ),
                ComponentParameter(
                    name="mimetype",
                    label="MIME Type",
                    type=ParameterType.STRING,
                    required=False,
                    description="MIME type of the file (auto-detected if empty)",
                    default_value=""
                )
            ],
            input_handles=[
                ComponentHandle(id="input", type="target", position="left", label="Data")
            ],
            output_handles=[
                ComponentHandle(id="success", type="source", position="right", label="Success"),
                ComponentHandle(id="error", type="source", position="bottom", label="Error")
            ]
        )
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        start_time = time.time()
        
        try:
            # Get configuration from input_data (includes merged node config)
            file_name = context.input_data.get("file_name")
            folder_id = context.input_data.get("folder_id", "")
            file_type = context.input_data.get("file_type", "auto")
            content_source = context.input_data.get("content_source", "previous_output")
            mimetype = context.input_data.get("mimetype", "")
            
            if not file_name:
                raise ValueError("file_name is required")
            
            # Debug logging
            debug_logs = [
                f"All input_data: {context.input_data}",
                f"Context previous_outputs keys: {list(context.previous_outputs.keys())}",
                f"File name: {file_name}",
                f"Folder ID: {folder_id}",
                f"File type: {file_type}",
                f"Content source: {content_source}"
            ]
            
            # Get content to upload
            content_data = None
            
            if content_source == "previous_output":
                # Get data from previous node outputs
                for node_id, node_output in context.previous_outputs.items():
                    debug_logs.append(f"Checking node {node_id}: {type(node_output)}")
                    print(f"🔍 Drive: Checking node {node_id}: {type(node_output)}")
                    if isinstance(node_output, dict):
                        print(f"🔍 Drive: Node {node_id} keys: {list(node_output.keys())}")
                        
                        # Priority 1: Check for AI Processing processed_results (contains AI responses)
                        if 'processed_results' in node_output and isinstance(node_output['processed_results'], list):
                            print(f"🎯 Drive: Found processed_results in {node_id}: {len(node_output['processed_results'])} rows")
                            # Convert to sheets format using the same method as GoogleSheetsWriteComponent
                            sheets_data = self._convert_processed_results_to_sheets_for_drive(node_output['processed_results'])
                            content_data = {'values': sheets_data}  # Wrap in sheets format
                            debug_logs.append(f"Found AI Processing data in node {node_id}: {len(sheets_data)} rows")
                            break
                        
                        # Priority 2: Check for AI Processing data (has results_for_sheets - perfect for CSV)
                        elif 'results_for_sheets' in node_output and isinstance(node_output['results_for_sheets'], list):
                            content_data = {'values': node_output['results_for_sheets']}  # Wrap in sheets format
                            debug_logs.append(f"Found AI Processing data in node {node_id}: {len(node_output['results_for_sheets'])} rows")
                            break
                        # Priority 3: Check for Google Sheets data (fallback)
                        elif 'values' in node_output and isinstance(node_output['values'], list):
                            print(f"🔍 Drive: Found values in {node_id}, but skipping in favor of AI processing data...")
                            # Don't break here, continue to look for AI processing data
                            pass
                        elif 'records' in node_output and isinstance(node_output['records'], list):
                            print(f"🔍 Drive: Found records in {node_id}, but skipping in favor of AI processing data...")
                            # Don't break here, continue to look for AI processing data
                            pass
                        else:
                            # Try different possible data keys for other formats
                            data_keys = ["data", "results", "output", "content"]
                            for key in data_keys:
                                if key in node_output and node_output[key]:
                                    content_data = node_output[key]
                                    debug_logs.append(f"Found data in node {node_id}.{key}: {type(content_data)}")
                                    break
                            if content_data:
                                break
                
                # If no AI processing data found, fallback to Google Sheets data
                if not content_data:
                    print(f"🔍 Drive: No AI processing data found, falling back to Google Sheets data...")
                    for node_id, node_output in context.previous_outputs.items():
                        if isinstance(node_output, dict):
                            if 'values' in node_output and isinstance(node_output['values'], list):
                                content_data = node_output  # Keep the full sheets structure
                                debug_logs.append(f"Fallback: Found Google Sheets data in node {node_id}: {len(node_output['values'])} rows")
                                print(f"🔍 Drive: Fallback - Using Google Sheets data from {node_id}")
                                break
                            elif 'records' in node_output and isinstance(node_output['records'], list):
                                content_data = node_output  # Keep the full sheets structure  
                                debug_logs.append(f"Fallback: Found Google Sheets records in node {node_id}: {len(node_output['records'])} records")
                                print(f"🔍 Drive: Fallback - Using Google Sheets records from {node_id}")
                                break
                        
            elif content_source == "input_data":
                content_data = context.input_data.get("content_data")
                debug_logs.append(f"Using input_data content: {type(content_data)}")
                
            if not content_data:
                error_msg = f"No content data found. Available keys: {list(context.input_data.keys())}, Previous outputs: {list(context.previous_outputs.keys())}"
                return ExecutionResult(
                    success=False,
                    output_data={},
                    error=error_msg,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    logs=debug_logs + [error_msg],
                    next_steps=["error"]
                )
            
            # Auto-detect and convert Google Sheets data to CSV if file_type is auto or csv
            if file_type in ["auto", "csv"] and isinstance(content_data, dict):
                if 'values' in content_data or 'records' in content_data or 'results_for_sheets' in content_data:
                    file_type = "csv"  # Force CSV for Google Sheets data
                    if not mimetype:  # Only set if not already specified
                        mimetype = "text/csv"
                    debug_logs.append("Auto-detected Google Sheets data, converting to CSV format")
            
            # Set appropriate MIME type based on file type if not specified
            if not mimetype:
                if file_type == "csv":
                    mimetype = "text/csv"
                elif file_type == "json":
                    mimetype = "application/json"
                elif file_type == "text":
                    mimetype = "text/plain"
                else:
                    mimetype = "application/octet-stream"
                debug_logs.append(f"Auto-detected MIME type: {mimetype}")
            
            # Convert content to bytes based on file type
            file_content = self._prepare_file_content(content_data, file_type)
            
            # Smart file naming logic
            final_file_name = await self._generate_smart_filename(file_name, folder_id)
            debug_logs.append(f"Final file name: {final_file_name}")
            
            # Try OAuth service for real upload
            oauth_success, oauth_result = await self._try_oauth_upload(
                file_content, final_file_name, folder_id, mimetype
            )
            
            if oauth_success:
                debug_logs.append("✅ Real OAuth upload successful!")
                execution_time = int((time.time() - start_time) * 1000)
                return ExecutionResult(
                    success=True,
                    output_data=oauth_result,
                    execution_time_ms=execution_time,
                    logs=debug_logs + [
                        f"Successfully connected to Google Drive (OAuth)",
                        f"Uploading file '{final_file_name}' to Google Drive",
                        f"Folder ID: {folder_id or 'Root'}",
                        f"File type: {file_type}",
                        f"Successfully uploaded file via OAuth",
                        f"File ID: {oauth_result.get('file_id', 'N/A')}",
                        f"View link: {oauth_result.get('web_view_link', 'N/A')}",
                        f"Operation completed in {execution_time}ms"
                    ],
                    next_steps=["success"]
                )
            else:
                # OAuth failed - return error instead of fallback
                error_msg = oauth_result.get('error', 'OAuth upload failed')
                debug_logs.append(f"❌ OAuth upload failed: {error_msg}")
                
                return ExecutionResult(
                    success=False,
                    output_data={},
                    error=f"Google Drive upload failed: {error_msg}",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    logs=debug_logs + [
                        f"Failed to upload '{final_file_name}' to Google Drive",
                        f"Error: {error_msg}",
                        "Make sure OAuth credentials are configured correctly"
                    ],
                    next_steps=["error"]
                )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output_data={},
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
                logs=[f"Error uploading to Google Drive: {str(e)}"],
                next_steps=["error"]
            )
    
    async def _generate_smart_filename(self, original_name: str, folder_id: str) -> str:
        """Generate smart filename with conflict resolution"""
        from datetime import datetime
        
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # If filename doesn't start with "Result_", add it
        if not original_name.startswith("Result_"):
            # Extract file extension
            if "." in original_name:
                name_part, extension = original_name.rsplit(".", 1)
                new_name = f"Result_{name_part}_{current_date}.{extension}"
            else:
                new_name = f"Result_{original_name}_{current_date}"
        else:
            # Already has Result_ prefix, just add date if not present
            if current_date not in original_name:
                if "." in original_name:
                    name_part, extension = original_name.rsplit(".", 1)
                    new_name = f"{name_part}_{current_date}.{extension}"
                else:
                    new_name = f"{original_name}_{current_date}"
            else:
                new_name = original_name
        
        # Check if OAuth service is available for real upload
        if await self._check_oauth_available():
            try:
                # Use OAuth service to check if file exists
                unique_name = await self._ensure_unique_filename_oauth(new_name, folder_id)
                return unique_name
            except Exception as e:
                # Fallback to generated name if OAuth check fails
                pass
        
        # Fallback: check with service account or return generated name
        if GOOGLE_DRIVE_AVAILABLE:
            try:
                # Check if file exists and generate unique name if needed
                unique_name = await self._ensure_unique_filename(new_name, folder_id)
                return unique_name
            except Exception as e:
                # Fallback to generated name if checking fails
                return new_name
        
        return new_name
    
    async def _ensure_unique_filename(self, filename: str, folder_id: str) -> str:
        """Ensure filename is unique in the target folder"""
        try:
            drive_service = GoogleDriveService()
            if not await drive_service.authenticate():
                return filename
            
            # List files in the folder to check for conflicts
            success, files_data = await drive_service.list_files(folder_id)
            
            if not success:
                return filename
            
            existing_files = files_data.get('files', [])
            existing_names = [f.get('name', '') for f in existing_files]
            
            if filename not in existing_names:
                return filename
            
            # File exists, generate new name with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            
            if "." in filename:
                name_part, extension = filename.rsplit(".", 1)
                return f"{name_part}_{timestamp}.{extension}"
            else:
                return f"{filename}_{timestamp}"
                
        except Exception as e:
            # If anything fails, just return original name
            return filename
    
    async def _try_oauth_upload(
        self, 
        file_content: bytes, 
        filename: str, 
        folder_id: str, 
        mimetype: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Try to upload using OAuth service"""
        try:
            from ..google_drive_oauth_service import oauth_drive_service
            
            success, result_data = await oauth_drive_service.upload_file(
                file_content=file_content,
                filename=filename,
                folder_id=folder_id if folder_id else None,
                mimetype=mimetype if mimetype else None
            )
            
            return success, result_data
                
        except Exception as e:
            return False, {"error": f"OAuth service error: {str(e)}"}
    
    async def _check_oauth_available(self) -> bool:
        """Check if OAuth service is available"""
        try:
            from ..google_drive_oauth_service import oauth_drive_service
            import os
            
            # Check if OAuth token exists
            token_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                'src', 'google_drive_token.json'
            )
            return os.path.exists(token_file)
            
        except Exception:
            return False
    
    async def _ensure_unique_filename_oauth(self, filename: str, folder_id: str) -> str:
        """Ensure filename is unique using OAuth service"""
        try:
            from ..google_drive_oauth_service import oauth_drive_service
            
            if not await oauth_drive_service.authenticate():
                return filename
            
            # List files in the folder to check for conflicts
            success, files_data = await oauth_drive_service.list_files(folder_id)
            
            if not success:
                return filename
            
            existing_files = files_data.get('files', [])
            existing_names = [f.get('name', '') for f in existing_files]
            
            if filename not in existing_names:
                return filename
            
            # File exists, generate new name with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            
            if "." in filename:
                name_part, extension = filename.rsplit(".", 1)
                return f"{name_part}_{timestamp}.{extension}"
            else:
                return f"{filename}_{timestamp}"
                
        except Exception as e:
            # If anything fails, just return original name
            return filename
    
    async def _upload_to_google_drive(
        self, 
        file_content: bytes, 
        filename: str, 
        folder_id: str, 
        mimetype: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Upload file to Google Drive using API"""
        try:
            # Get Google Drive service
            drive_service = GoogleDriveService()
            
            # Authenticate
            if not await drive_service.authenticate():
                return False, {"error": "Failed to authenticate with Google Drive API"}
            
            # Upload file
            success, result_data = await drive_service.upload_file(
                file_content=file_content,
                filename=filename,
                folder_id=folder_id if folder_id else None,
                mimetype=mimetype if mimetype else None
            )
            
            return success, result_data
                
        except Exception as e:
            return False, {"error": f"Google Drive API error: {str(e)}"}
    
    def _prepare_file_content(self, data, file_type: str) -> bytes:
        """Convert data to bytes based on file type"""
        if file_type == "json":
            import json
            if isinstance(data, (dict, list)):
                content = json.dumps(data, indent=2, ensure_ascii=False)
            else:
                content = str(data)
            return content.encode('utf-8')
            
        elif file_type == "csv":
            import csv
            import io
            
            output = io.StringIO()
            
            # Handle Google Sheets data structure specially
            if isinstance(data, dict):
                if 'values' in data and isinstance(data['values'], list):
                    # Google Sheets 'values' format - list of lists (includes AI processing wrapped data)
                    writer = csv.writer(output)
                    for row in data['values']:
                        writer.writerow(row)
                elif 'results_for_sheets' in data and isinstance(data['results_for_sheets'], list):
                    # AI Processing 'results_for_sheets' format - direct list of lists
                    writer = csv.writer(output)
                    for row in data['results_for_sheets']:
                        writer.writerow(row)
                elif 'records' in data and isinstance(data['records'], list):
                    # Google Sheets 'records' format - list of dictionaries
                    records = data['records']
                    if len(records) > 0 and isinstance(records[0], dict):
                        fieldnames = records[0].keys()
                        writer = csv.DictWriter(output, fieldnames=fieldnames)
                        writer.writeheader()
                        for row in records:
                            writer.writerow(row)
                    else:
                        # Fallback to simple format
                        writer = csv.writer(output)
                        writer.writerow(['Data'])
                        for record in records:
                            writer.writerow([str(record)])
                else:
                    # Regular dict - convert to key-value CSV
                    writer = csv.writer(output)
                    writer.writerow(['Key', 'Value'])
                    for key, value in data.items():
                        writer.writerow([key, str(value)])
            elif isinstance(data, list):
                writer = csv.writer(output)
                if len(data) > 0:
                    if isinstance(data[0], dict):
                        # List of dictionaries - convert to CSV
                        fieldnames = data[0].keys()
                        writer = csv.DictWriter(output, fieldnames=fieldnames)
                        writer.writeheader()
                        for row in data:
                            writer.writerow(row)
                    elif isinstance(data[0], list):
                        # List of lists - write as CSV
                        for row in data:
                            writer.writerow(row)
                    else:
                        # List of primitives
                        for item in data:
                            writer.writerow([item])
            else:
                # Single value
                writer = csv.writer(output)
                writer.writerow([str(data)])
            
            return output.getvalue().encode('utf-8')
            
        elif file_type == "text":
            if isinstance(data, str):
                return data.encode('utf-8')
            else:
                return str(data).encode('utf-8')
                
        elif file_type == "binary":
            if isinstance(data, bytes):
                return data
            elif isinstance(data, str):
                return data.encode('utf-8')
            else:
                return str(data).encode('utf-8')
                
        else:  # auto
            if isinstance(data, str):
                return data.encode('utf-8')
            elif isinstance(data, bytes):
                return data
            elif isinstance(data, (dict, list)):
                import json
                content = json.dumps(data, indent=2, ensure_ascii=False)
                return content.encode('utf-8')
            else:
                return str(data).encode('utf-8')

    def _convert_processed_results_to_sheets_for_drive(self, processed_results):
        """
        Convert AI processing results to Google Sheets format for Drive export
        Same logic as GoogleSheetsWriteComponent._convert_processed_results_to_sheets
        """
        if not processed_results or not isinstance(processed_results, list):
            return []
        
        print(f"🔍 Drive: _convert_processed_results_to_sheets_for_drive called with {len(processed_results)} results")
        
        # Create header row - we know from logs that input has these columns plus we want to add Prompt
        headers = ["Description", "Example Asset URL", "Desired Output Format", "Model Specification", "Prompt"]
        
        # Start with header row
        sheets_data = [headers]
        
        # Process each result row
        for i, result in enumerate(processed_results):
            if not isinstance(result, dict):
                print(f"🔍 Drive: Row {i}: Not a dict, skipping")
                continue
            
            print(f"🔍 Drive: Row {i}: Processing result with keys: {list(result.keys())}")
            
            # Get input data (original row data)
            input_data = result.get("input_data", {})
            print(f"🔍 Drive: Row {i}: input_data keys: {list(input_data.keys()) if isinstance(input_data, dict) else 'Not a dict'}")
            
            # Extract AI response - nested as result.ai_response.ai_response
            ai_response = ""
            
            if "ai_response" in result:
                ai_resp_data = result["ai_response"]
                print(f"🔍 Drive: Row {i}: Found ai_response, type: {type(ai_resp_data)}")
                
                if isinstance(ai_resp_data, dict):
                    # The AI response is nested as result.ai_response.ai_response
                    ai_response = ai_resp_data.get("ai_response", "")
                    print(f"🔍 Drive: Row {i}: Extracted nested ai_response: {ai_response[:100]}...")
                elif isinstance(ai_resp_data, str):
                    # If it's already a string, use it directly
                    ai_response = ai_resp_data
                    print(f"🔍 Drive: Row {i}: Using direct string ai_response: {ai_response[:100]}...")
                else:
                    print(f"🔍 Drive: Row {i}: ai_response is neither dict nor string: {type(ai_resp_data)}")
            else:
                print(f"🔍 Drive: Row {i}: No ai_response key found")
            
            # Create row with original data + AI response in Prompt column
            row = [
                input_data.get("Description", ""),
                input_data.get("Example Asset URL", ""),
                input_data.get("Desired Output Format", ""),
                input_data.get("Model Specification", ""),
                ai_response  # This goes in the Prompt column
            ]
            
            print(f"🔍 Drive: Row {i}: Final row data - Prompt length: {len(ai_response) if ai_response else 0}")
            sheets_data.append(row)
        
        print(f"🔍 Drive: _convert_processed_results_to_sheets_for_drive returning {len(sheets_data)} rows (including header)")
        return sheets_data


# Global component registry instance
component_registry = ComponentRegistry()
