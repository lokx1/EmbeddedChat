#!/usr/bin/env python3
"""
Create a simple workflow configuration with correct worksheet name
"""

import json

def create_workflow_config():
    """Create workflow config that can be imported into frontend"""
    print("🔧 CREATING WORKFLOW CONFIG FOR TEST_NEW WORKSHEET")
    print("="*55)
    
    workflow_config = {
        "name": "AI Processing to TEST_NEW Worksheet",
        "description": "Read from TEST_NEW, process with AI, write back to TEST_NEW with Prompt column",
        "components": [
            {
                "id": "manual_trigger",
                "type": "manual_trigger",
                "position": {"x": 100, "y": 200},
                "config": {
                    "label": "Start",
                    "type": "manual_trigger",
                    "configuration": {}
                }
            },
            {
                "id": "google_sheets_read",
                "type": "google_sheets",
                "position": {"x": 300, "y": 200},
                "config": {
                    "label": "Read from TEST_NEW",
                    "type": "google_sheets",
                    "configuration": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "worksheet_name": "TEST_NEW",
                        "range": "A:Z"
                    }
                }
            },
            {
                "id": "ai_processing",
                "type": "ai_processing",
                "position": {"x": 500, "y": 200},
                "config": {
                    "label": "AI Processing",
                    "type": "ai_processing",
                    "configuration": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "prompt_template": "Create a detailed and comprehensive prompt for generating: {{Description}}. Consider the desired output format: {{Desired Output Format}}. Requirements: {{Model Specification}}"
                    }
                }
            },
            {
                "id": "google_sheets_write",
                "type": "google_sheets_write",
                "position": {"x": 700, "y": 200},
                "config": {
                    "label": "Write to TEST_NEW",
                    "type": "google_sheets_write",
                    "configuration": {
                        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                        "worksheet_name": "TEST_NEW",
                        "operation": "overwrite"
                    }
                }
            }
        ],
        "connections": [
            {
                "source": "manual_trigger",
                "target": "google_sheets_read"
            },
            {
                "source": "google_sheets_read", 
                "target": "ai_processing"
            },
            {
                "source": "ai_processing",
                "target": "google_sheets_write"
            }
        ]
    }
    
    # Save to file
    config_file = "workflow_config_test_new.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(workflow_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Workflow config saved to: {config_file}")
    print(f"📋 Components:")
    for comp in workflow_config['components']:
        comp_type = comp['type']
        comp_label = comp['config']['label']
        print(f"   🔸 {comp_label} ({comp_type})")
        
        if comp_type in ['google_sheets', 'google_sheets_write']:
            worksheet = comp['config']['configuration'].get('worksheet_name', 'NOT SET')
            print(f"      📄 Worksheet: {worksheet}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Copy the workflow config from {config_file}")
    print(f"2. Import it into the frontend workflow editor")
    print(f"3. Execute the workflow")
    print(f"4. Check TEST_NEW worksheet for AI responses in Prompt column")
    
    return config_file

def show_manual_instructions():
    """Show manual instructions for fixing the issue"""
    print(f"\n📋 MANUAL FIX INSTRUCTIONS:")
    print(f"="*35)
    print(f"1. Open frontend workflow editor")
    print(f"2. Create new workflow or edit existing one")
    print(f"3. For Google Sheets READ component:")
    print(f"   - Set worksheet_name = 'TEST_NEW'")
    print(f"4. For Google Sheets WRITE component:")
    print(f"   - Set worksheet_name = 'TEST_NEW'")
    print(f"5. Execute workflow")
    print(f"6. Check TEST_NEW worksheet - Prompt column should have AI responses")
    
    print(f"\n🔍 CURRENT PROBLEM:")
    print(f"- AI Processing ✅ (creates Prompt column)")
    print(f"- Google Sheets Write ✅ (writes successfully)")
    print(f"- Worksheet Target ❌ (writes to TEST121 instead of TEST_NEW)")

if __name__ == "__main__":
    config_file = create_workflow_config()
    show_manual_instructions()
    
    print(f"\n💡 SUMMARY:")
    print(f"The workflow IS working! It just needs to target the correct worksheet.")
    print(f"AI_Response is being written as 'Prompt' column, but to the wrong worksheet.")
