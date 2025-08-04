#!/usr/bin/env python3
"""
Check backend server status and AI response processing logic
"""
import requests
import json

def check_backend_status():
    """Check if backend is running and test the AI processing components"""
    
    print("=== Backend Status Check ===")
    
    try:
        # Check backend health
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"⚠️ Backend health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        print("Please start the backend with: cd backend && python main.py")
        return False
    
    try:
        # Check available components
        components_response = requests.get('http://localhost:8000/api/v1/workflow/components', timeout=10)
        if components_response.status_code == 200:
            components = components_response.json()
            print(f"✅ Found {len(components)} workflow components")
            
            # Check for AI processing component
            ai_component = None
            sheets_write_component = None
            for comp in components:
                if comp.get('type') == 'ai_processing':
                    ai_component = comp
                elif comp.get('type') == 'google_sheets_write':
                    sheets_write_component = comp
            
            if ai_component:
                print("✅ AI Processing component available")
            else:
                print("❌ AI Processing component not found")
                
            if sheets_write_component:
                print("✅ Google Sheets Write component available")
            else:
                print("❌ Google Sheets Write component not found")
                
        else:
            print(f"❌ Components check failed: {components_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Components check error: {e}")
        return False
    
    # Check if Ollama is running (for AI processing)
    try:
        ollama_response = requests.get('http://localhost:11434/api/tags', timeout=3)
        if ollama_response.status_code == 200:
            models = ollama_response.json()
            print(f"✅ Ollama is running with {len(models.get('models', []))} models")
        else:
            print("⚠️ Ollama not accessible - AI processing will use simulation")
    except:
        print("⚠️ Ollama not running - AI processing will use simulation")
    
    return True

def show_recent_workflows():
    """Show recent workflow executions"""
    try:
        instances_response = requests.get('http://localhost:8000/api/v1/workflow/instances', timeout=10)
        if instances_response.status_code == 200:
            instances = instances_response.json()
            print(f"\n📋 Recent workflow instances: {len(instances)}")
            for instance in instances[-3:]:  # Show last 3
                instance_id = instance.get('id')
                name = instance.get('name', 'Unnamed')
                status = instance.get('status', 'unknown')
                print(f"   {instance_id}: {name} - {status}")
        else:
            print(f"❌ Could not fetch instances: {instances_response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching instances: {e}")

if __name__ == "__main__":
    if check_backend_status():
        show_recent_workflows()
        print("\n🎯 Backend is ready for testing!")
        print("You can now run: python test_backend_ai_extraction.py")
    else:
        print("\n❌ Backend is not ready. Please start it first.")
