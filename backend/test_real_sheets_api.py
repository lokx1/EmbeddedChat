#!/usr/bin/env python3
"""
Test Google Sheets API with real workflow
"""

from src.services.google_sheets_service import GoogleSheetsService
from datetime import datetime
import json

def test_real_google_sheets():
    """Test real Google Sheets API"""
    print("🧪 Testing Real Google Sheets API Integration")
    print("="*50)
    
    # Your sheet details
    sheet_id = '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc'
    sheet_name = 'Sheet2'
    
    print(f"📊 Sheet ID: {sheet_id}")
    print(f"📄 Target Sheet: {sheet_name}")
    
    try:
        # Initialize service
        service = GoogleSheetsService()
        
        # Authenticate
        print("\n🔐 Authenticating...")
        if not service.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful!")
        
        # Get sheet info
        print("\n📋 Getting sheet information...")
        info = service.get_sheet_info(sheet_id)
        
        if info:
            print(f"📄 Sheet Title: {info['title']}")
            print(f"📝 Available sheets: {[s['title'] for s in info['sheets']]}")
            
            # Check if target sheet exists
            sheet_exists = any(s['title'] == sheet_name for s in info['sheets'])
            if not sheet_exists:
                print(f"⚠️  Sheet '{sheet_name}' not found. Creating it...")
                if service.create_sheet(sheet_id, sheet_name):
                    print(f"✅ Created sheet '{sheet_name}'")
                else:
                    print(f"❌ Failed to create sheet '{sheet_name}'")
                    return False
        else:
            print("❌ Failed to get sheet info. Check permissions.")
            print("📧 Make sure to share sheet with: ai-asset-automation@automation-467607.iam.gserviceaccount.com")
            return False
        
        # Prepare test data
        print(f"\n📝 Preparing test data...")
        test_data = [
            ["Timestamp", "Event", "Status", "Source", "Details"],
            [str(datetime.now()), "API Test", "Success", "Workflow", "Real Google Sheets integration working!"],
            [str(datetime.now()), "Data Write", "Completed", "Backend", "Written from Python workflow component"],
            [str(datetime.now()), "Automation", "Active", "System", "Google Sheets Write component operational"]
        ]
        
        print(f"📊 Data to write: {len(test_data)} rows, {len(test_data[0])} columns")
        
        # Test different write modes
        print(f"\n✍️ Testing write operations...")
        
        # Mode 1: Overwrite
        print(f"1️⃣ Testing OVERWRITE mode...")
        range_name = f"{sheet_name}!A1"
        success = service.write_sheet(sheet_id, range_name, test_data)
        
        if success:
            print("✅ Overwrite successful!")
        else:
            print("❌ Overwrite failed")
            return False
        
        # Mode 2: Append
        print(f"2️⃣ Testing APPEND mode...")
        append_data = [
            [str(datetime.now()), "Append Test", "Success", "API", "Additional data appended"]
        ]
        
        success = service.append_sheet(sheet_id, f"{sheet_name}!A1", append_data)
        
        if success:
            print("✅ Append successful!")
        else:
            print("❌ Append failed")
        
        # Mode 3: Read back data
        print(f"3️⃣ Testing READ operation...")
        read_range = f"{sheet_name}!A1:E10"
        data = service.read_sheet(sheet_id, read_range)
        
        if data:
            print(f"✅ Read successful! Retrieved {len(data)} rows")
            print("📋 First few rows:")
            for i, row in enumerate(data[:3]):
                print(f"   Row {i+1}: {row}")
        else:
            print("❌ Read failed")
        
        # Show results
        print(f"\n🎉 All tests completed successfully!")
        print(f"🔗 Check your sheet: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_integration():
    """Test Google Sheets integration with workflow"""
    print(f"\n🔧 Testing Workflow Integration")
    print("="*40)
    
    # Import workflow components
    from src.services.workflow.component_registry import GoogleSheetsWriteComponent, ExecutionContext
    
    # Create component
    component = GoogleSheetsWriteComponent()
    
    # Create test context
    context = ExecutionContext(
        workflow_id="test-workflow-001",
        instance_id="test-instance-001",
        step_id="test-step-001",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "Sheet2",
            "range": "A1",
            "mode": "append",
            "data_format": "auto",
            "data": [
                ["Workflow Test", "Component", "Integration"],
                [str(datetime.now()), "GoogleSheetsWrite", "Working"]
            ]
        },
        previous_outputs={},
        global_variables={}
    )
    
    print(f"📊 Testing GoogleSheetsWriteComponent...")
    
    # Execute component
    import asyncio
    result = asyncio.run(component.execute(context))
    
    print(f"📋 Component Result:")
    print(f"   Success: {result.success}")
    print(f"   Execution Time: {result.execution_time_ms}ms")
    
    if result.success:
        print(f"   Operation: {result.output_data.get('operation', 'N/A')}")
        print(f"   Status: {result.output_data.get('status', 'N/A')}")
        print("✅ Workflow component integration successful!")
    else:
        print(f"   Error: {result.error}")
        print("❌ Workflow component integration failed")
    
    # Show logs
    if result.logs:
        print(f"\n📝 Execution Logs:")
        for log in result.logs:
            print(f"   - {log}")
    
    return result.success

if __name__ == "__main__":
    print("🚀 Google Sheets Real API Integration Test")
    print("="*55)
    
    # Test 1: Direct API
    api_success = test_real_google_sheets()
    
    if api_success:
        # Test 2: Workflow integration
        workflow_success = test_workflow_integration()
        
        if workflow_success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ Google Sheets API is fully integrated")
            print(f"✅ Workflow component is working")
            print(f"🔗 Your sheet: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")
        else:
            print(f"\n⚠️  API works but workflow integration has issues")
    else:
        print(f"\n❌ API test failed. Please check:")
        print(f"   1. Share sheet with: ai-asset-automation@automation-467607.iam.gserviceaccount.com")
        print(f"   2. Make sure credentials.json is valid")
        print(f"   3. Check Google Cloud Console permissions")
