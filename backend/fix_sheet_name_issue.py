#!/usr/bin/env python3
"""
Fix sheet name issue and test workflow
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.google_sheets_service import get_sheets_service

def fix_sheet_issue():
    """Fix the sheet name issue"""
    
    print("🔧 Fixing Sheet Name Issue")
    print("=" * 40)
    
    sheets_service = get_sheets_service()
    if not sheets_service.authenticate():
        print("❌ Authentication failed")
        return False
        
    sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    # Test different sheet names
    test_names = ["Test", "Result_Test", "Sheet1"]
    
    for sheet_name in test_names:
        try:
            print(f"Testing sheet name: {sheet_name}")
            data = sheets_service.read_sheet(sheet_id, f"{sheet_name}!A1:A1")
            print(f"✅ '{sheet_name}' EXISTS and accessible")
            
            # If Result_Test exists, let's use it for frontend
            if sheet_name == "Result_Test":
                print(f"💡 SOLUTION: Frontend should use '{sheet_name}' instead of 'Test'")
                return sheet_name
                
        except Exception as e:
            print(f"❌ '{sheet_name}' error: {str(e)[:100]}...")
    
    # Try to create Test sheet
    print(f"\n🛠️ Creating 'Test' sheet...")
    try:
        # Use simple approach - try to write headers to Test sheet
        headers = [["Name", "Value", "Timestamp", "Status"]]
        success = sheets_service.write_sheet(sheet_id, "Test!A1", headers)
        
        if success:
            print(f"✅ 'Test' sheet created with headers!")
            return "Test"
        else:
            print(f"❌ Failed to create 'Test' sheet")
            
    except Exception as e:
        print(f"❌ Error creating 'Test' sheet: {e}")
    
    return None

def test_workflow_with_correct_sheet():
    """Test workflow execution with correct sheet name"""
    
    print(f"\n🧪 Testing Workflow with Correct Configuration")
    print("=" * 50)
    
    import requests
    import json
    from datetime import datetime
    
    base_url = "http://localhost:8000/api/v1"
    
    # Use Result_Test (known to exist)
    correct_sheet_name = "Result_Test"
    
    workflow_data = {
        "nodes": [
            {
                "id": "start-1",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "type": "manual_trigger", 
                    "config": {
                        "trigger_data": {
                            "test": "corrected workflow",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                }
            },
            {
                "id": "write-1", 
                "type": "google_sheets_write",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Write to Correct Sheet",
                    "type": "google_sheets_write",
                    "config": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "sheet_name": correct_sheet_name,  # Use existing sheet
                        "range": "A1",
                        "mode": "append",
                        "data_format": "auto"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "start-1", 
                "target": "write-1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }
    
    # Create and execute workflow
    template_payload = {
        "name": "CORRECTED Sheet Name Test",
        "description": "Test with correct sheet name",
        "workflow_data": workflow_data,
        "category": "test"
    }
    
    template_response = requests.post(f"{base_url}/workflow/editor/save", json=template_payload)
    if template_response.status_code == 200:
        template_data = template_response.json()
        template_id = template_data["data"]["workflow_id"]
        
        instance_payload = {
            "name": f"Corrected Test {datetime.now().strftime('%H:%M:%S')}",
            "template_id": template_id,
            "workflow_data": workflow_data,
            "input_data": {
                "data": [
                    ["Name", "Status", "Timestamp"],
                    ["Corrected Test", "Success", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                ]
            }
        }
        
        instance_response = requests.post(f"{base_url}/workflow/instances", json=instance_payload)
        if instance_response.status_code == 200:
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            
            execute_response = requests.post(f"{base_url}/workflow/instances/{instance_id}/execute")
            if execute_response.status_code == 200:
                print(f"✅ Corrected workflow executed!")
                print(f"📋 Instance ID: {instance_id}")
                print(f"📝 Using sheet: {correct_sheet_name}")
                return True
                
    print(f"❌ Corrected workflow failed")
    return False

if __name__ == "__main__":
    print("🎯 FIXING FRONTEND SHEET NAME ISSUE")
    print("=" * 60)
    
    # Fix sheet issue
    working_sheet = fix_sheet_issue()
    
    # Test corrected workflow
    if working_sheet:
        success = test_workflow_with_correct_sheet()
        
        print(f"\n" + "=" * 60) 
        print(f"🎯 FINAL DIAGNOSIS & SOLUTION")
        print(f"=" * 60)
        
        if working_sheet == "Test":
            print(f"✅ 'Test' sheet created successfully")
            print(f"💡 Frontend config is CORRECT")
            print(f"🔧 Try executing workflow from frontend again")
        else:
            print(f"❌ 'Test' sheet creation failed")
            print(f"✅ '{working_sheet}' sheet is available")
            print(f"🔧 FRONTEND FIX REQUIRED:")
            print(f"   Change Sheet Name from 'Test' to '{working_sheet}'")
            print(f"   In frontend workflow config panel")
            
        print(f"\n🔗 Google Sheets: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")
    else:
        print(f"\n❌ Unable to resolve sheet name issue")
        print(f"🔧 Manual fix required: Create 'Test' sheet in Google Sheets")
