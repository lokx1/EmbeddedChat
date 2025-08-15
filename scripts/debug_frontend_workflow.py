#!/usr/bin/env python3
"""
Debug the frontend workflow execution issue
"""

import requests
import json
import time
from datetime import datetime

def debug_running_workflows():
    """Check all running workflow instances"""
    base_url = "http://localhost:8000/api/v1/workflow"
    
    print("🔍 Checking all workflow instances...")
    
    # Get all instances
    instances_response = requests.get(f"{base_url}/instances")
    if instances_response.status_code == 200:
        instances_data = instances_response.json()
        instances = instances_data.get("data", {}).get("instances", [])
        
        print(f"📊 Found {len(instances)} workflow instances")
        
        running_instances = []
        for instance in instances:
            print(f"\n📋 Instance: {instance['id']}")
            print(f"   Name: {instance['name']}")
            print(f"   Status: {instance['status']}")
            print(f"   Created: {instance.get('created_at', 'N/A')}")
            print(f"   Updated: {instance.get('updated_at', 'N/A')}")
            
            if instance['status'] in ['running', 'executing']:
                running_instances.append(instance)
                
        if running_instances:
            print(f"\n⚠️  Found {len(running_instances)} running instances!")
            
            for instance in running_instances:
                print(f"\n🔍 Debugging instance: {instance['id']}")
                debug_instance_execution(instance['id'])
        else:
            print("\n✅ No running instances found")
            
    else:
        print(f"❌ Failed to get instances: {instances_response.text}")

def debug_instance_execution(instance_id):
    """Debug a specific instance execution"""
    base_url = "http://localhost:8000/api/v1/workflow"
    
    # Get instance details
    instance_response = requests.get(f"{base_url}/instances/{instance_id}")
    if instance_response.status_code == 200:
        instance_data = instance_response.json()
        instance = instance_data["data"]["instance"]
        
        print(f"📊 Instance Status: {instance['status']}")
        
        if instance.get('output_data'):
            print("📤 Current Output:")
            output = instance['output_data']
            if 'node_outputs' in output:
                for node_id, node_output in output['node_outputs'].items():
                    print(f"   Node {node_id}: {node_output.get('status', 'unknown')}")
                    
        if instance.get('error_message'):
            print(f"❌ Error: {instance['error_message']}")
            
        # Get execution logs
        logs_response = requests.get(f"{base_url}/instances/{instance_id}/logs")
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            steps = logs_data.get("data", {}).get("steps", [])
            
            print(f"📝 Execution Steps ({len(steps)}):")
            for step in steps[-10:]:  # Show last 10 steps
                print(f"   [{step['created_at']}] {step['step_type']}: {step['status']}")
                if step.get('error_message'):
                    print(f"      Error: {step['error_message']}")
                if step.get('logs'):
                    for log in step['logs'][-3:]:  # Show last 3 logs per step
                        print(f"      Log: {log}")
                        
        # Try to stop if running too long
        if instance['status'] in ['running', 'executing']:
            print(f"\n⚠️  Instance has been running since: {instance.get('updated_at', 'unknown')}")
            print("Would you like to stop this instance? (This script won't stop it automatically)")
            
    else:
        print(f"❌ Failed to get instance details: {instance_response.text}")

def check_ollama_status():
    """Check if Ollama is running and working"""
    print("\n🤖 Checking Ollama status...")
    
    try:
        import requests
        ollama_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if ollama_response.status_code == 200:
            models = ollama_response.json().get("models", [])
            print(f"✅ Ollama running with {len(models)} models")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model['name']}")
        else:
            print(f"⚠️  Ollama responded with status: {ollama_response.status_code}")
    except Exception as e:
        print(f"❌ Ollama not accessible: {str(e)}")
        print("This might cause AI Processing steps to hang!")

def check_google_sheets_config():
    """Check Google Sheets configuration"""
    print("\n📊 Checking Google Sheets configuration...")
    
    try:
        # Check if credentials file exists
        import os
        creds_path = "credentials.json"
        if os.path.exists(creds_path):
            print(f"✅ Credentials file found: {creds_path}")
        else:
            print(f"⚠️  Credentials file not found: {creds_path}")
            
        # Try to import Google services
        try:
            from src.services.workflow.google_services import GoogleSheetsService
            print("✅ Google Sheets service can be imported")
        except Exception as e:
            print(f"❌ Google Sheets service import failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Google Sheets check failed: {str(e)}")

if __name__ == "__main__":
    print("=== Debugging Frontend Workflow Execution ===\n")
    
    # Check system status
    check_ollama_status()
    check_google_sheets_config()
    
    # Debug running workflows
    debug_running_workflows()
    
    print("\n" + "="*50)
    print("🔧 Debug Summary:")
    print("1. Check if any workflows are stuck in 'running' status")
    print("2. Verify Ollama is running for AI Processing")
    print("3. Confirm Google Sheets credentials are configured")
    print("4. Look for error messages in execution logs")
    print("\n💡 If workflows are stuck:")
    print("   - Stop Ollama if it's causing issues")
    print("   - Restart backend server")
    print("   - Use frontend to cancel stuck workflows")
