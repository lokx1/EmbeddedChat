"""
Test GoogleSheetsWriteComponent with records data format
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.workflow.component_registry import GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def test_records_format():
    """Test GoogleSheetsWriteComponent with records data format"""
    print("🔍 Testing GoogleSheetsWriteComponent with records format...")
    
    # Create execution context with records data (like from sheets-read)
    context = ExecutionContext(
        workflow_id="test-workflow",
        instance_id="test-instance", 
        step_id="test-step",
        input_data={
            # Node config data
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "TestRecords",
            "range": "A1",
            "mode": "append",
            "data_format": "auto"
        },
        previous_outputs={
            "sheets-read-2": {
                "records": [
                    {
                        "Description": "Design a Task Manager app logo",
                        "Example Asset URL": "https://static.wikia.nocookie.net/logopedia/images/9/97/Task_Manager_2024.png",
                        "Desired Output Format": "PNG",
                        "Model Specification": "OpenAI"
                    },
                    {
                        "Description": "Summer Sale banner for a fashion store", 
                        "Example Asset URL": "https://images.vexels.com/content/107842/preview/summer-sale-poster-design-illustration-836fb3.png",
                        "Desired Output Format": "JPG",
                        "Model Specification": "Claude"
                    },
                    {
                        "Description": "MP3 audio notification \"Order Confirmed\"",
                        "Example Asset URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRj5MiCGTOkXy7kd-lzuznvzGSJqDXPPAJfDA&s",
                        "Desired Output Format": "MP3 audio",
                        "Model Specification": "Claude"
                    },
                    {
                        "Description": "Video thumbnail \"Product Tutorial\"",
                        "Example Asset URL": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQjf4lMrFSaMJgODN9lJK0shVZiiRulk3nmCQ&s",
                        "Desired Output Format": "PNG", 
                        "Model Specification": "OpenAI"
                    }
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
    result = asyncio.run(test_records_format())
