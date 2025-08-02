#!/usr/bin/env python3
"""
Monitor Test Workflow and Check Results
"""

import requests
import time
from src.services.google_sheets_service import GoogleSheetsService

def monitor_test_execution():
    """Monitor the simple test workflow execution"""
    print("⏳ Monitoring Test Workflow Execution")
    print("="*45)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Look for the Simple Write Test Instance
    for i in range(30):  # Monitor for 30 seconds
        try:
            response = requests.get(f"{base_url}/instances")
            
            if response.status_code == 200:
                data = response.json()
                instances = data.get("data", {}).get("instances", [])
                
                # Find our test instance
                test_instances = [
                    inst for inst in instances 
                    if "Simple Write Test" in inst.get("name", "")
                ]
                
                if test_instances:
                    latest_test = test_instances[0]
                    status = latest_test.get("status", "unknown")
                    name = latest_test.get("name", "Unknown")
                    instance_id = latest_test.get("id")
                    
                    print(f"   Check {i+1}/30: {name} - {status}")
                    
                    if status in ["completed", "failed"]:
                        print(f"\n🎯 Test workflow {status}!")
                        
                        # Get detailed results
                        detail_response = requests.get(f"{base_url}/instances/{instance_id}")
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            instance = detail_data.get("data", {}).get("instance", {})
                            
                            if status == "completed":
                                print(f"✅ Execution successful!")
                                
                                # Check output data
                                output_data = instance.get('output_data', {})
                                if output_data:
                                    node_outputs = output_data.get('node_outputs', {})
                                    print(f"   Node outputs: {list(node_outputs.keys())}")
                                    
                                    # Check write node specifically
                                    write_node_output = None
                                    for node_id, output in node_outputs.items():
                                        if 'write' in node_id.lower():
                                            write_node_output = output
                                            break
                                    
                                    if write_node_output:
                                        print(f"   📊 Write node output: {write_node_output}")
                                    else:
                                        print(f"   ⚠️  No write node output found")
                            else:
                                error_msg = instance.get('error_message', 'Unknown error')
                                print(f"❌ Execution failed: {error_msg}")
                        
                        return status == "completed"
                    
                    elif status == "running":
                        print(f"   Still processing...")
                else:
                    print(f"   No test instances found")
        
        except Exception as e:
            print(f"   Error checking: {str(e)}")
        
        time.sleep(1)
    
    print(f"\n⏰ Monitoring timeout")
    return False

def check_sheets_results():
    """Check if data was written to Google Sheets"""
    print(f"\n📊 Checking Google Sheets Results")
    print("="*35)
    
    try:
        service = GoogleSheetsService()
        
        if service.authenticate():
            # Check Result_Test sheet
            results = service.read_sheet(
                "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                "Result_Test!A1:L10"
            )
            
            if results:
                print(f"✅ Result_Test sheet accessible")
                print(f"   Total rows: {len(results)}")
                
                if len(results) > 1:
                    print(f"   Headers: {results[0][:4]}...")
                    print(f"   Data rows: {len(results) - 1}")
                    
                    # Show recent data
                    for i, row in enumerate(results[1:3], 1):  # Show first 2 data rows
                        print(f"   Row {i}: {row[:4]}...")
                        
                    return True
                else:
                    print(f"   Only headers found - no data written yet")
                    return False
            else:
                print(f"❌ Could not read Result_Test sheet")
                return False
        else:
            print(f"❌ Google Sheets authentication failed")
            return False
    
    except Exception as e:
        print(f"❌ Error checking sheets: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Test Workflow Results Monitor")
    print("="*40)
    
    # Monitor execution
    success = monitor_test_execution()
    
    # Check sheets results
    sheets_success = check_sheets_results()
    
    print(f"\n🎯 Test Results Summary:")
    print(f"   Workflow execution: {'✅ Success' if success else '❌ Failed'}")
    print(f"   Google Sheets write: {'✅ Success' if sheets_success else '❌ Failed'}")
    
    if success and sheets_success:
        print(f"\n🎉 WORKFLOW SYSTEM WORKING!")
        print(f"✅ Both execution and Google Sheets write successful")
    elif success and not sheets_success:
        print(f"\n⚠️  EXECUTION OK, SHEETS WRITE ISSUE")
        print(f"   Workflow runs but doesn't write to sheets")
    else:
        print(f"\n❌ WORKFLOW EXECUTION ISSUE")
        print(f"   Backend execution engine has problems")
