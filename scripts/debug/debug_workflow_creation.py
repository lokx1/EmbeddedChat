#!/usr/bin/env python3
"""
Debug Workflow Creation
"""

import requests
import json

def test_simple_workflow():
    """Test creating a simple workflow"""
    print("🔍 TESTING SIMPLE WORKFLOW CREATION")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Simple workflow template
    simple_template = {
        "name": "Simple Test Workflow",
        "description": "Simple test",
        "components": [
            {
                "id": "manual_trigger",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 100},
                "config": {
                    "label": "Manual Trigger",
                    "type": "manual_trigger",
                    "configuration": {}
                }
            }
        ],
        "connections": []
    }
    
    try:
        print("📤 Sending simple template...")
        template_response = requests.post(
            f"{base_url}/workflow/templates",
            json=simple_template
        )
        
        print(f"📥 Response status: {template_response.status_code}")
        
        if template_response.status_code == 201:
            print("✅ Simple workflow template created successfully")
            return True
        else:
            print(f"❌ Failed to create simple template")
            print(f"Response: {template_response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_existing_workflow():
    """Get existing workflow templates"""
    print("\n🔍 CHECKING EXISTING WORKFLOWS")
    print("="*40)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        templates_response = requests.get(f"{base_url}/workflow/templates")
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            templates = templates_data.get("data", [])
            
            print(f"📊 Found {len(templates)} existing templates:")
            
            for template in templates[-5:]:  # Show last 5
                template_id = template["id"]
                template_name = template["name"]
                components_count = len(template.get("components", []))
                
                print(f"   🔸 {template_name} ({template_id[:8]}...) - {components_count} components")
                
                # Check if it has google_sheets_write component
                has_sheets_write = False
                for comp in template.get("components", []):
                    if comp.get("type") == "google_sheets_write":
                        has_sheets_write = True
                        config = comp.get("config", {}).get("configuration", {})
                        worksheet_name = config.get("worksheet_name", "NOT SET")
                        print(f"      📝 Has sheets_write, worksheet: {worksheet_name}")
                        break
                
                if not has_sheets_write:
                    print(f"      ❌ No sheets_write component")
            
            return templates
        
        else:
            print(f"❌ Failed to get templates: {templates_response.status_code}")
            return []
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return []

if __name__ == "__main__":
    # Test simple workflow creation first
    simple_success = test_simple_workflow()
    
    # Check existing workflows
    existing_templates = test_existing_workflow()
    
    if simple_success:
        print("\n✅ Backend can create workflows")
    else:
        print("\n❌ Backend has issues creating workflows")
