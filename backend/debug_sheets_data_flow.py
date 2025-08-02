#!/usr/bin/env python3
"""
Debug GoogleSheetsWriteComponent data flow
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.workflow.component_registry import GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext


async def test_component_with_data():
    """Test GoogleSheetsWriteComponent with different data scenarios"""
    
    component = GoogleSheetsWriteComponent()
    
    print("=== Testing GoogleSheetsWriteComponent Data Flow ===")
    
    # Test 1: Data in input_data
    print("\n🧪 Test 1: Data in input_data")
    test_data = [
        ["Name", "Age", "City"],
        ["Debug Test 1", "25", "Test City"]
    ]
    
    context1 = ExecutionContext(
        workflow_id="test-workflow-1",
        instance_id="test-instance-1",
        step_id="step-1",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",  # CORRECT sheet ID
            "sheet_name": "Result_Test",
            "range": "A1",
            "mode": "append",
            "data_format": "auto",
            "data": test_data  # Data directly in input_data
        },
        previous_outputs={},
        global_variables={}
    )
    
    print(f"Input data: {context1.input_data.get('data', 'NO DATA')}")
    print(f"Previous outputs: {context1.previous_outputs}")
    
    try:
        result1 = await component.execute(context1)
        print(f"✅ Test 1 Result:")
        print(f"   Success: {result1.success}")
        print(f"   Status: {result1.output_data.get('status', 'unknown')}")
        if result1.logs:
            print(f"   Last log: {result1.logs[-1]}")
    except Exception as e:
        print(f"❌ Test 1 Error: {e}")
    
    # Test 2: Data in previous_outputs
    print("\n🧪 Test 2: Data in previous_outputs")
    
    context2 = ExecutionContext(
        workflow_id="test-workflow-2",
        instance_id="test-instance-2", 
        step_id="step-2",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",  # CORRECT sheet ID
            "sheet_name": "Result_Test",
            "range": "A5",
            "mode": "append",
            "data_format": "auto"
        },
        previous_outputs={
            "data": [
                ["Name", "Age", "City"], 
                ["Debug Test 2", "30", "Previous City"]
            ]
        },
        global_variables={}
    )
    
    print(f"Input data: {context2.input_data.get('data', 'NO DATA')}")
    print(f"Previous outputs: {context2.previous_outputs.get('data', 'NO DATA')}")
    
    try:
        result2 = await component.execute(context2)
        print(f"✅ Test 2 Result:")
        print(f"   Success: {result2.success}")
        print(f"   Status: {result2.output_data.get('status', 'unknown')}")
        if result2.logs:
            print(f"   Last log: {result2.logs[-1]}")
    except Exception as e:
        print(f"❌ Test 2 Error: {e}")
    
    # Test 3: No data (should fail)
    print("\n🧪 Test 3: No data (should fail)")
    
    context3 = ExecutionContext(
        workflow_id="test-workflow-3",
        instance_id="test-instance-3",
        step_id="step-3", 
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",  # CORRECT sheet ID
            "sheet_name": "Result_Test",
            "range": "A10",
            "mode": "append",
            "data_format": "auto"
        },
        previous_outputs={},
        global_variables={}
    )
    
    print(f"Input data: {context3.input_data.get('data', 'NO DATA')}")
    print(f"Previous outputs: {context3.previous_outputs.get('data', 'NO DATA')}")
    
    try:
        result3 = await component.execute(context3)
        print(f"✅ Test 3 Result:")
        print(f"   Success: {result3.success}")
        print(f"   Error: {result3.error}")
    except Exception as e:
        print(f"❌ Test 3 Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_component_with_data())
