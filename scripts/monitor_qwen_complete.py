#!/usr/bin/env python3
"""
Create Qwen Results Sheet and Monitor
"""

from src.services.google_sheets_service import GoogleSheetsService
import time
import requests

def create_qwen_results_sheet():
    """Create Qwen_Results sheet if it doesn't exist"""
    print("🛠️  Creating Qwen_Results Sheet")
    print("="*35)
    
    try:
        service = GoogleSheetsService()
        
        if service.authenticate():
            # Create Qwen_Results sheet with headers
            headers = [
                "Row", "Description", "Format", "Status", "AI_Response", 
                "Provider", "Model", "Generated_URL", "Processing_Time", 
                "Quality", "Timestamp", "Metadata"
            ]
            
            # Try to create the sheet
            success = service.create_sheet(
                "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                "Qwen_Results"
            )
            
            if success:
                print("✅ Qwen_Results sheet created")
                
                # Add headers
                header_success = service.write_sheet(
                    "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "Qwen_Results!A1:L1",
                    [headers]
                )
                
                if header_success:
                    print("✅ Headers added to Qwen_Results sheet")
                else:
                    print("⚠️  Could not add headers")
            else:
                print("⚠️  Sheet may already exist or creation failed")
        else:
            print("❌ Could not authenticate")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def monitor_workflow_completion():
    """Monitor workflow until completion"""
    print(f"\n⏳ Monitoring Workflow Completion")
    print("="*35)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    for i in range(60):  # Monitor for 60 checks (2 minutes)
        try:
            response = requests.get(f"{base_url}/instances")
            
            if response.status_code == 200:
                data = response.json()
                instances = data.get("data", {}).get("instances", [])
                
                # Find latest Qwen instance
                qwen_instances = [
                    inst for inst in instances 
                    if "qwen" in inst.get("name", "").lower()
                ]
                
                if qwen_instances:
                    latest = qwen_instances[0]  # Most recent first
                    status = latest.get("status", "unknown")
                    name = latest.get("name", "Unnamed")
                    
                    print(f"   Check {i+1}/60: {name} - {status}")
                    
                    if status in ["completed", "failed"]:
                        print(f"\n🎯 Workflow {status}!")
                        
                        if status == "completed":
                            print(f"✅ Checking results...")
                            check_final_results()
                        else:
                            error = latest.get("error_message", "Unknown error")
                            print(f"❌ Error: {error}")
                        break
                    elif status == "running":
                        print(f"   Still processing...")
                else:
                    print(f"   No Qwen instances found")
        
        except Exception as e:
            print(f"   Error checking status: {str(e)}")
        
        time.sleep(2)  # Wait 2 seconds
    else:
        print(f"\n⏰ Monitoring timeout after 2 minutes")

def check_final_results():
    """Check final results in Google Sheets"""
    print(f"\n🔍 Checking Final Results")
    print("="*30)
    
    try:
        service = GoogleSheetsService()
        
        if service.authenticate():
            results = service.read_sheet(
                "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                "Qwen_Results!A1:L10"
            )
            
            if results and len(results) > 1:
                print(f"✅ Found {len(results)-1} result rows")
                
                # Check if real Ollama was used
                real_ollama_count = 0
                simulation_count = 0
                
                for row in results[1:]:
                    if len(row) > 4:
                        ai_response = row[4] if len(row) > 4 else ""
                        provider = row[5] if len(row) > 5 else ""
                        
                        if "ollama" in provider.lower() and "qwen" in ai_response.lower():
                            real_ollama_count += 1
                            print(f"🎯 Real Ollama detected in row!")
                        elif "simulation" in ai_response.lower() or "demo" in provider.lower():
                            simulation_count += 1
                
                print(f"\n📊 Results Summary:")
                print(f"   🤖 Real Ollama responses: {real_ollama_count}")
                print(f"   🎭 Simulation responses: {simulation_count}")
                
                if real_ollama_count > 0:
                    print(f"\n🎉 SUCCESS: Real Ollama integration working!")
                else:
                    print(f"\n⚠️  Only simulation responses found")
            else:
                print(f"❌ No results found in sheet")
    
    except Exception as e:
        print(f"❌ Error checking results: {str(e)}")

if __name__ == "__main__":
    print("🚀 Qwen Workflow Monitor & Results Checker")
    print("="*50)
    
    # Step 1: Create sheet
    create_qwen_results_sheet()
    
    # Step 2: Monitor completion
    monitor_workflow_completion()
    
    print(f"\n🎯 Monitoring Complete!")
    print(f"🔗 Check Google Sheets: https://docs.google.com/spreadsheets/d/1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc/edit")
