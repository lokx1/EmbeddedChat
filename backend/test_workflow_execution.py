#!/usr/bin/env python3
"""
Test thực tế workflow execution với Google Sheets Write
"""

import asyncio
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.workflow.component_registry import component_registry
from src.schemas.workflow_components import ExecutionContext

async def test_workflow_execution():
    print("=== Test Workflow Execution ===")
    
    # Test workflow data (tương tự demo_workflow.json)
    workflow_data = {
        "nodes": [
            {
                "id": "node_1",
                "type": "sheets",
                "data": {
                    "label": "Google Sheets Read",
                    "config": {
                        "sheet_id": "test_sheet_id",
                        "sheet_name": "Sheet1",
                        "range": "A:E"
                    }
                }
            },
            {
                "id": "node_2", 
                "type": "ai_processing",
                "data": {
                    "label": "AI Processing",
                    "config": {
                        "provider": "qwen",
                        "prompt": "Analyze this data: {data}"
                    }
                }
            },
            {
                "id": "node_3",
                "type": "google_sheets_write",
                "data": {
                    "label": "Google Sheets Write",
                    "config": {
                        "sheet_id": "test_sheet_id",
                        "sheet_name": "Sheet1",
                        "range": "A1"
                    }
                }
            }
        ],
        "edges": [
            {"source": "node_1", "target": "node_2"},
            {"source": "node_2", "target": "node_3"}
        ]
    }
    
    # Test get component
    try:
        component_class = component_registry.get_component("google_sheets_write")
        print(f"✓ Found GoogleSheetsWriteComponent: {component_class}")
        
        # Test metadata
        metadata = component_class.get_metadata()
        print(f"✓ Component type: {metadata.type}")
        print(f"✓ Component name: {metadata.name}")
        
        # Test component creation
        component = component_class()
        print(f"✓ Component instance created: {component}")
        
    except Exception as e:
        print(f"✗ Error with google_sheets_write component: {e}")
        return
    
    # Test all required components
    required_components = ["sheets", "ai_processing", "google_sheets_write"]
    
    for comp_type in required_components:
        try:
            comp_class = component_registry.get_component(comp_type)
            print(f"✓ Component '{comp_type}' found: {comp_class}")
        except Exception as e:
            print(f"✗ Component '{comp_type}' not found: {e}")
    
    print("\n=== Component Registry Status ===")
    all_components = component_registry.get_all_components()
    for comp in all_components:
        print(f"- {comp.type}: {comp.name}")
    
    # Test mock execution context
    print("\n=== Test Mock Execution ===")
    try:
        context = ExecutionContext(
            workflow_id="test_workflow",
            instance_id="test_instance", 
            step_id="node_3",
            input_data={
                "sheet_id": "test_sheet_id",
                "sheet_name": "Sheet1",
                "range": "A1"
            },
            previous_outputs={
                "node_2": {
                    "results_for_sheets": [
                        ["Description", "Asset", "Prompt"],
                        ["Test data", "test.png", "This is a test AI response"]
                    ]
                }
            },
            global_variables={}
        )
        
        # Tạo GoogleSheetsWriteComponent instance
        sheets_write = component_registry.get_component("google_sheets_write")()
        print(f"✓ Created GoogleSheetsWriteComponent instance")
        
        # Mock execution (không thực sự gọi Google API)
        print(f"✓ Context prepared for execution")
        print(f"  - Input data: {context.input_data}")
        print(f"  - Previous outputs: {context.previous_outputs}")
        
    except Exception as e:
        print(f"✗ Error in mock execution: {e}")

if __name__ == "__main__":
    asyncio.run(test_workflow_execution())

from src.services.workflow.component_registry import ComponentRegistry
from src.models.workflow import WorkflowInstance


async def test_google_sheets_workflow():
    """Test the Google Sheets component execution directly"""
    
    print("🚀 Starting Google Sheets Component Test")
    print("=" * 50)
    
    try:
        # Test component metadata first
        print("\n📋 Testing Component Metadata...")
        registry = ComponentRegistry()
        component = registry.get_component("google_sheets")
        
        if component:
            metadata = component.get_metadata()
            print(f"✅ Component found: {metadata.name}")
            print(f"   Description: {metadata.description}")
            print(f"   Parameters: {len(metadata.parameters)}")
            
            # Test component execution
            print("\n🔧 Testing Component Execution...")
            
            # Create minimal execution context
            from src.schemas.workflow_components import ExecutionContext
            
            context = ExecutionContext(
                workflow_id="test-workflow",
                instance_id="test-instance",
                step_id="test-step",
                input_data={
                    "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "sheet_name": "Sheet1",
                    "range": "A1:Z1000"
                },
                previous_outputs={},
                global_variables={}
            )
            
            # Execute the component
            component_instance = component()  # Instantiate the component
            result = await component_instance.execute(context)
            
            print(f"\n📊 Execution Result:")
            print(f"   Success: {result.success}")
            
            if result.success:
                output_data = result.output_data
                print(f"   Output Keys: {list(output_data.keys())}")
                
                if 'records' in output_data:
                    records = output_data['records']
                    print(f"   Records: {len(records)}")
                    
                    # Show first few records
                    if records:
                        print(f"\n📋 Sample Data (first 3 records):")
                        for i, record in enumerate(records[:3]):
                            print(f"     Record {i+1}: {record}")
                
                if 'spreadsheet_info' in output_data:
                    info = output_data['spreadsheet_info']
                    print(f"   Columns: {', '.join(info.get('columns', []))}")
                    print(f"   Total Rows: {info.get('total_rows', 0)}")
                    print(f"   Total Columns: {info.get('total_columns', 0)}")
                    
                # Show logs
                if result.logs:
                    print(f"\n📝 Execution Logs:")
                    for log in result.logs:
                        print(f"   - {log}")
                        
            else:
                print(f"   Error: {result.error}")
                
        else:
            print("❌ Component not found!")
            return
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete")


if __name__ == "__main__":
    asyncio.run(test_google_sheets_workflow())
