#!/usr/bin/env python3
"""
Monitor Qwen Workflow Results
"""

import requests
import time
from src.services.google_sheets_service import GoogleSheetsService

def monitor_qwen_results():
    """Monitor the Qwen workflow execution and results"""
    print("🔍 Monitoring Qwen Workflow Results")
    print("="*45)
    
    # Check Google Sheets results
    print("📊 Checking Google Sheets results...")
    
    try:
        service = GoogleSheetsService()
        
        if service.authenticate():
            # Check Qwen_Results sheet
            results = service.read_sheet(
                "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                "Qwen_Results!A1:L10"
            )
            
            if results:
                print(f"✅ Found {len(results)} rows in Qwen_Results sheet")
                
                # Display latest results
                if len(results) > 1:
                    print(f"\n📋 Latest Results:")
                    headers = results[0] if results[0] else []
                    
                    for i, row in enumerate(results[1:6], 1):  # Show first 5 data rows
                        print(f"\n   Row {i}:")
                        for j, cell in enumerate(row[:8]):  # Show first 8 columns
                            header = headers[j] if j < len(headers) else f"Col{j+1}"
                            print(f"     {header}: {cell}")
                
                # Check for AI response data
                ai_responses = []
                for row in results[1:]:
                    if len(row) > 4:  # Assuming AI response is in column 5+
                        ai_response = row[4] if len(row) > 4 else ""
                        if ai_response and len(ai_response) > 50:
                            ai_responses.append(ai_response[:200] + "...")
                
                if ai_responses:
                    print(f"\n🤖 AI Responses Found: {len(ai_responses)}")
                    for i, response in enumerate(ai_responses[:3], 1):
                        print(f"   Response {i}: {response}")
                        
                        # Check if it's from Ollama (real) or simulation
                        if "qwen" in response.lower() or "ollama" in response.lower():
                            print(f"     🎯 REAL OLLAMA DETECTED!")
                        elif "simulated" in response.lower() or "demo" in response.lower():
                            print(f"     ⚠️  Simulation mode detected")
                        else:
                            print(f"     ❓ Response type unclear")
                else:
                    print(f"⚠️  No substantial AI responses found")
            else:
                print("❌ No results found in Qwen_Results sheet")
        else:
            print("❌ Could not authenticate with Google Sheets")
    
    except Exception as e:
        print(f"❌ Error checking Google Sheets: {str(e)}")
    
    # Check recent instances via API
    print(f"\n🔍 Checking Recent Workflow Instances...")
    
    try:
        base_url = "http://localhost:8000/api/v1/workflow"
        
        response = requests.get(f"{base_url}/instances")
        
        if response.status_code == 200:
            data = response.json()
            instances = data.get("data", {}).get("instances", [])
            
            # Find recent Qwen instances
            qwen_instances = [
                inst for inst in instances 
                if "qwen" in inst.get("name", "").lower()
            ]
            
            print(f"✅ Found {len(qwen_instances)} Qwen instances")
            
            for instance in qwen_instances[:3]:  # Show last 3
                print(f"\n   Instance: {instance.get('name', 'Unnamed')}")
                print(f"   Status: {instance.get('status', 'unknown')}")
                print(f"   Created: {instance.get('created_at', 'unknown')}")
                
                if instance.get('output_data'):
                    output = instance.get('output_data', {})
                    if 'processed_results' in output:
                        results_count = len(output.get('processed_results', []))
                        print(f"   Processed Results: {results_count}")
                
                if instance.get('error_message'):
                    print(f"   Error: {instance.get('error_message')}")
        else:
            print(f"❌ API request failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error checking API: {str(e)}")

if __name__ == "__main__":
    print("🚀 Qwen Workflow Results Monitor")
    print("="*40)
    
    monitor_qwen_results()
    
    print(f"\n🎯 Summary:")
    print(f"✅ Check complete")
    print(f"🔗 Google Sheets: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")
    print(f"📊 Check 'Qwen_Results' tab for AI processing outputs")
