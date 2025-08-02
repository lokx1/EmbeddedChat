#!/usr/bin/env python3
"""
Debug script to test GoogleSheetsWriteComponent directly
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the backend src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.workflow.component_registry import GoogleSheetsWriteComponent, ExecutionContext


async def test_sheets_write():
    """Test GoogleSheetsWriteComponent directly"""
    print("=== Testing GoogleSheetsWriteComponent ===")
    
    component = GoogleSheetsWriteComponent()
    
    # Test data
    test_data = [
        ["Name", "Age", "City"],
        ["Test User", "25", "Test City"],
        ["Another User", "30", "Another City"]
    ]
    
    # Create execution context
    context = ExecutionContext(
        input_data={
            "sheet_id": "1QH86P8_g1v7iDTrV5aZrxwl-MdOQJgdC6H4I8xKVaZw",  # Your sheet ID
            "sheet_name": "Result_Test",
            "range": "A1",
            "mode": "append",
            "data_format": "auto",
            "data": test_data
        },
        previous_outputs={"data": test_data},
        workflow_instance_id="test-debug-001",
        node_id="test-write-node"
    )
    
    print(f"Input data: {context.input_data}")
    print(f"Previous outputs: {context.previous_outputs}")
    
    # Execute component
    try:
        result = await component.execute(context)
        print(f"\n=== Execution Result ===")
        print(f"Success: {result.success}")
        print(f"Output data: {result.output_data}")
        print(f"Execution time: {result.execution_time_ms}ms")
        print(f"Error: {result.error}")
        print(f"Next steps: {result.next_steps}")
        
        print(f"\n=== Logs ===")
        for log in result.logs:
            print(f"  - {log}")
            
        # Check if it's simulation or real API
        if result.output_data.get("status") == "simulated":
            print("\n⚠️  WARNING: Component used simulation mode!")
        elif result.output_data.get("status") == "success":
            print("\n✅ SUCCESS: Component used real Google Sheets API!")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_google_sheets_api_directly():
    """Test Google Sheets API directly"""
    print("\n=== Testing Google Sheets API directly ===")
    
    try:
        from services.google_sheets_service import get_sheets_service
        
        # Get service
        sheets_service = get_sheets_service()
        print(f"Service created: {type(sheets_service)}")
        
        # Test authentication
        auth_result = sheets_service.authenticate()
        print(f"Authentication: {auth_result}")
        
        if auth_result:
            # Test simple write
            sheet_id = "1QH86P8_g1v7iDTrV5aZrxwl-MdOQJgdC6H4I8xKVaZw"
            range_name = "Result_Test!A10"
            test_data = [["Debug Test", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]
            
            write_result = sheets_service.write_sheet(sheet_id, range_name, test_data)
            print(f"Direct write result: {write_result}")
            
            return write_result
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API directly: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("Starting GoogleSheetsWriteComponent debug test...")
    
    # Test 1: Direct API test
    api_result = await test_google_sheets_api_directly()
    
    # Test 2: Component test
    component_result = await test_sheets_write()
    
    print(f"\n=== Summary ===")
    print(f"Direct API test: {'✅ PASS' if api_result else '❌ FAIL'}")
    print(f"Component test: {'✅ PASS' if component_result and component_result.success else '❌ FAIL'}")
    
    if component_result and component_result.output_data.get("status") == "simulated":
        print("🔍 Component is using simulation mode - need to investigate why API fails")
    elif component_result and component_result.output_data.get("status") == "success":
        print("✅ Component is using real API successfully")


if __name__ == "__main__":
    asyncio.run(main())
