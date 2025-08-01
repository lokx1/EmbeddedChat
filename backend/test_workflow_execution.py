"""
Test Google Sheets Workflow Execution
"""
import asyncio
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
