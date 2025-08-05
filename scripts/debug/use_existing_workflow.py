#!/usr/bin/env python3
"""
Use existing workflow and modify worksheet name
"""

import requests
import json

def create_instance_with_worksheet():
    """Create instance from existing template with specific worksheet"""
    print("🔍 USING EXISTING WORKFLOW WITH WORKSHEET NAME")
    print("="*55)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Use the most recent AI to Sheets template
    template_id = "1643d9b9-82a7-4fe0-a56d-11f96a922d0f"  # AI -> Sheets Test
    
    try:
        # Get template details first
        template_response = requests.get(f"{base_url}/workflow/templates/{template_id}")
        
        if template_response.status_code == 200:
            template_data = template_response.json()
            template = template_data["data"]
            
            print(f"📋 Using template: {template['name']}")
            print(f"📊 Components: {len(template.get('components', []))}")
            
            # Show components
            for comp in template.get('components', []):
                comp_type = comp.get('type', 'unknown')
                print(f"   🔸 {comp_type}")
                
                if comp_type == 'google_sheets_write':
                    config = comp.get('config', {}).get('configuration', {})
                    current_worksheet = config.get('worksheet_name', 'NOT SET')
                    print(f"      Current worksheet: {current_worksheet}")
            
            # Create instance
            instance_data = {
                "name": "AI to Sheets with TEST_NEW - " + 
                       __import__('datetime').datetime.now().strftime("%H:%M:%S"),
                "description": "Test AI processing with TEST_NEW worksheet",
                "template_id": template_id,
                "config_overrides": {
                    "google_sheets_write": {
                        "worksheet_name": "TEST_NEW"
                    },
                    "google_sheets": {
                        "worksheet_name": "TEST_NEW"  # Also change read source
                    }
                }
            }
            
            print(f"\n🚀 Creating instance with worksheet: TEST_NEW")
            
            instance_response = requests.post(
                f"{base_url}/workflow/instances",
                json=instance_data
            )
            
            if instance_response.status_code == 201:
                instance_resp_data = instance_response.json()
                instance_id = instance_resp_data["data"]["id"]
                print(f"✅ Created instance: {instance_id}")
                
                # Execute workflow
                execute_response = requests.post(
                    f"{base_url}/workflow/instances/{instance_id}/execute"
                )
                
                if execute_response.status_code == 200:
                    print(f"🚀 Workflow execution started!")
                    return instance_id
                
                else:
                    print(f"❌ Failed to execute: {execute_response.status_code}")
                    print(f"Response: {execute_response.text}")
                    return None
            
            else:
                print(f"❌ Failed to create instance: {instance_response.status_code}")
                print(f"Response: {instance_response.text}")
                return None
        
        else:
            print(f"❌ Failed to get template: {template_response.status_code}")
            return None
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

if __name__ == "__main__":
    instance_id = create_instance_with_worksheet()
    
    if instance_id:
        print(f"\n🎯 Instance created: {instance_id}")
        print(f"📍 Check worksheet 'TEST_NEW' for results!")
    else:
        print(f"\n❌ Failed to create instance")
