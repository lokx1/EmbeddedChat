#!/usr/bin/env python3
"""
Debug script to test GoogleSheetsWriteComponent directly
"""
import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import modules
from services.workflow.component_registry import GoogleSheetsWriteComponent
from services.google_sheets_service import get_sheets_service
from api.schemas.workflow_components import ExecutionContext


async def test_google_sheets_api_directly():
    """Test Google Sheets API directly"""
    print("=== Testing Google Sheets API directly ===")
    
    try:
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
            
            print(f"Attempting to write: {test_data}")
            print(f"To range: {range_name}")
            
            write_result = sheets_service.write_sheet(sheet_id, range_name, test_data)
            print(f"Direct write result: {write_result}")
            
            if write_result:
                print("✅ Direct API write successful!")
            else:
                print("❌ Direct API write failed!")
            
            return write_result
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API directly: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sheets_write_component():
    """Test GoogleSheetsWriteComponent directly"""
    print("\n=== Testing GoogleSheetsWriteComponent ===")
    
    try:
        component = GoogleSheetsWriteComponent()
        
        # Test data
        test_data = [
            ["Name", "Age", "City", "Timestamp"],
            ["Test User", "25", "Test City", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        # Create execution context
        context = ExecutionContext(
            input_data={
                "sheet_id": "1QH86P8_g1v7iDTrV5aZrxwl-MdOQJgdC6H4I8xKVaZw",
                "sheet_name": "Result_Test",
                "range": "A1",
                "mode": "append",
                "data_format": "auto",
                "data": test_data
            },
            previous_outputs={"data": test_data},
            workflow_instance_id="test-debug-002",
            node_id="test-write-node"
        )
        
        print(f"Input data keys: {list(context.input_data.keys())}")
        print(f"Test data: {test_data}")
        
        # Execute component
        result = await component.execute(context)
        
        print(f"\n=== Component Execution Result ===")
        print(f"Success: {result.success}")
        print(f"Execution time: {result.execution_time_ms}ms")
        print(f"Error: {result.error}")
        print(f"Next steps: {result.next_steps}")
        
        print(f"\n=== Output Data ===")
        for key, value in result.output_data.items():
            print(f"  {key}: {value}")
        
        print(f"\n=== Logs ===")
        for i, log in enumerate(result.logs, 1):
            print(f"  {i}. {log}")
            
        # Check status
        status = result.output_data.get("status", "unknown")
        if status == "simulated":
            print("\n⚠️  WARNING: Component used SIMULATION mode!")
            print("   This means the Google Sheets API call failed and fell back to simulation.")
        elif status == "success":
            print("\n✅ SUCCESS: Component used real Google Sheets API!")
        else:
            print(f"\n❓ UNKNOWN: Component status: {status}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during component execution: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main test function"""
    print("Starting GoogleSheetsWriteComponent debug test...")
    print("=" * 60)
    
    # Test 1: Direct API test
    api_result = await test_google_sheets_api_directly()
    
    # Test 2: Component test
    component_result = await test_sheets_write_component()
    
    print(f"\n" + "=" * 60)
    print(f"=== FINAL SUMMARY ===")
    print(f"Direct API test: {'✅ PASS' if api_result else '❌ FAIL'}")
    
    if component_result:
        component_status = component_result.output_data.get("status", "unknown")
        print(f"Component test: {'✅ PASS' if component_result.success else '❌ FAIL'}")
        print(f"Component mode: {component_status}")
        
        if api_result and component_status == "simulated":
            print("\n🔍 ISSUE FOUND:")
            print("   - Direct API works fine")
            print("   - But component falls back to simulation")
            print("   - Need to check component's API integration logic")
        elif not api_result:
            print("\n🔍 ISSUE FOUND:")
            print("   - Direct API fails")
            print("   - Need to check authentication and API setup")
        elif component_status == "success":
            print("\n✅ ALL GOOD:")
            print("   - Both direct API and component work correctly")
    else:
        print(f"Component test: ❌ FAIL (Exception)")


if __name__ == "__main__":
    asyncio.run(main())
