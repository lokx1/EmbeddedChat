#!/usr/bin/env python3
"""
Fix GoogleSheetsWriteComponent issues and test with correct configuration
"""
import asyncio
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.workflow.component_registry import GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext


async def test_fixed_sheets_component():
    """Test GoogleSheetsWriteComponent with correct sheet ID and configuration"""
    
    print("🔧 FIXING GoogleSheetsWriteComponent Issues")
    print("=" * 50)
    
    component = GoogleSheetsWriteComponent()
    
    # Use the CORRECT sheet ID that works in all other scripts
    correct_sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    print(f"✅ Using CORRECT sheet ID: {correct_sheet_id}")
    print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{correct_sheet_id}/edit")
    
    # Test data from trigger node
    test_data = [
        ["Name", "Age", "City", "Timestamp"],
        ["Fixed Test User", "28", "Fixed City", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]
    
    # Simulate real workflow execution context
    context = ExecutionContext(
        workflow_id="fixed-workflow-001",
        instance_id="fixed-instance-001",
        step_id="sheets-write-step",
        input_data={
            "sheet_id": correct_sheet_id,
            "sheet_name": "Result_Test", 
            "range": "A1",
            "mode": "append",
            "data_format": "auto"
        },
        previous_outputs={
            "data": test_data  # Data from previous trigger/processing node
        },
        global_variables={}
    )
    
    print(f"\n🧪 Testing Component Execution")
    print(f"   Input data: {context.input_data.get('data', 'FROM PREVIOUS OUTPUTS')}")
    print(f"   Previous outputs data: {len(context.previous_outputs.get('data', []))} rows")
    
    try:
        start_time = time.time()
        result = await component.execute(context)
        end_time = time.time()
        
        print(f"\n📊 EXECUTION RESULT")
        print(f"   Success: {result.success}")
        print(f"   Execution time: {result.execution_time_ms}ms")
        print(f"   Actual time: {int((end_time - start_time) * 1000)}ms")
        
        # Check status
        status = result.output_data.get("status", "unknown")
        operation = result.output_data.get("operation", "unknown")
        
        if status == "success" and operation == "write_api":
            print(f"   ✅ SUCCESS: Real Google Sheets API used!")
            print(f"   📝 Data written: {result.output_data.get('data_written', {})}")
            
            if result.logs:
                print(f"\n📋 LOGS:")
                for i, log in enumerate(result.logs, 1):
                    print(f"     {i}. {log}")
                    
        elif status == "simulated":
            print(f"   ⚠️  SIMULATION: API failed, used simulation")
            print(f"   📝 Simulated data: {result.output_data.get('data_written', {})}")
            
            if result.logs:
                print(f"\n📋 LOGS:")
                for i, log in enumerate(result.logs, 1):
                    print(f"     {i}. {log}")
        else:
            print(f"   ❓ UNKNOWN STATUS: {status}")
            
        if result.error:
            print(f"   ❌ Error: {result.error}")
            
        return result.success and status == "success"
        
    except Exception as e:
        print(f"❌ EXECUTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function"""
    print("🚀 GoogleSheetsWriteComponent Fix & Test")
    print("=" * 60)
    
    success = await test_fixed_sheets_component()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 FINAL RESULT")
    if success:
        print("✅ GoogleSheetsWriteComponent WORKING with real API!")
        print("💡 Issue was incorrect sheet ID causing 404 errors")
        print("🔧 Frontend needs to use correct sheet ID in workflow config")
    else:
        print("❌ GoogleSheetsWriteComponent still has issues")
        print("🔍 Need further investigation")
        
    print(f"\n📋 NEXT STEPS:")
    print("1. Update frontend workflow config with correct sheet ID")
    print("2. Ensure all workflows use: 1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc")
    print("3. Test end-to-end workflow execution from frontend")


if __name__ == "__main__":
    asyncio.run(main())
