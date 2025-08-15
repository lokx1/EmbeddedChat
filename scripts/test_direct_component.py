"""
Direct test of GoogleSheetsWriteComponent to debug why simulation is used
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.workflow.component_registry import GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_direct_component():
    """Test GoogleSheetsWriteComponent directly"""
    print("🔍 Testing GoogleSheetsWriteComponent directly...")
    
    # Create execution context with config data
    context = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance", 
        step_id="test-step",
        input_data={
            # Node config data - Use the working sheet ID
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "Sheet1",
            "range": "A1",
            "mode": "append",
            "data_format": "auto",
            # Data to write
            "data": [
                ["Name", "Age", "City"],
                ["John Doe", "30", "New York"],
                ["Jane Smith", "25", "San Francisco"]
            ]
        },
        previous_outputs={
            "trigger-1": {
                "data": [
                    ["Name", "Age", "City"],
                    ["John Doe", "30", "New York"],
                    ["Jane Smith", "25", "San Francisco"]
                ]
            }
        },
        global_variables={}
    )
    
    # Create component and execute
    component = GoogleSheetsWriteComponent()
    result = await component.execute(context)
    
    print(f"📊 Execution Result:")
    print(f"   Success: {result.success}")
    print(f"   Output Data: {result.output_data}")
    print(f"   Error: {result.error}")
    print(f"   Execution Time: {result.execution_time_ms}ms")
    print(f"   Logs:")
    for log in result.logs:
        print(f"      - {log}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_direct_component())
