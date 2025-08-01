#!/usr/bin/env python3
"""
Create test data for AI Asset Generation workflow
"""

from src.services.google_sheets_service import GoogleSheetsService
from datetime import datetime

def create_test_data():
    """Create test data in Google Sheets for AI asset generation"""
    print("🧪 Creating Test Data for AI Asset Generation")
    print("="*50)
    
    # Your sheet details
    sheet_id = '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc'
    input_sheet = 'AI_Input_Data'
    
    # Test data for AI asset generation
    test_data = [
        # Header row
        ["description", "example_asset_url", "output_format", "ai_model", "priority", "notes"],
        
        # Test records
        [
            "A beautiful sunset over mountain landscape",
            "https://example.com/sunset_ref.jpg",
            "PNG",
            "OpenAI",
            "High",
            "For website hero section"
        ],
        [
            "Modern minimalist logo design for tech startup",
            "https://example.com/logo_ref.png",
            "PNG",
            "Claude",
            "High",
            "Company branding"
        ],
        [
            "Animated GIF of loading spinner",
            "https://example.com/spinner_ref.gif",
            "GIF",
            "OpenAI",
            "Medium",
            "UI component"
        ],
        [
            "Background music for meditation app",
            "https://example.com/meditation_ref.mp3",
            "MP3",
            "OpenAI",
            "Medium",
            "30 second loop"
        ],
        [
            "Product photo of wireless headphones",
            "https://example.com/headphones_ref.jpg",
            "JPG",
            "Claude",
            "High",
            "E-commerce listing"
        ],
        [
            "Cartoon character mascot for kids app",
            "https://example.com/mascot_ref.png",
            "PNG",
            "OpenAI",
            "Low",
            "Friendly and colorful"
        ],
        [
            "Corporate presentation template",
            "https://example.com/template_ref.pptx",
            "PNG",
            "Claude",
            "Medium",
            "Professional style"
        ]
    ]
    
    try:
        # Initialize service
        service = GoogleSheetsService()
        
        # Authenticate
        print("🔐 Authenticating...")
        if not service.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful!")
        
        # Check if input sheet exists, create if not
        print(f"\n📋 Checking sheet '{input_sheet}'...")
        info = service.get_sheet_info(sheet_id)
        
        if info:
            sheet_exists = any(s['title'] == input_sheet for s in info['sheets'])
            if not sheet_exists:
                print(f"⚠️  Sheet '{input_sheet}' not found. Creating it...")
                if service.create_sheet(sheet_id, input_sheet):
                    print(f"✅ Created sheet '{input_sheet}'")
                else:
                    print(f"❌ Failed to create sheet '{input_sheet}'")
                    return False
            else:
                print(f"✅ Sheet '{input_sheet}' already exists")
        
        # Write test data
        print(f"\n📝 Writing test data...")
        range_name = f"{input_sheet}!A1"
        success = service.write_sheet(sheet_id, range_name, test_data)
        
        if success:
            print(f"✅ Successfully wrote {len(test_data)} rows to sheet!")
            print(f"📊 Data includes:")
            print(f"   - {len(test_data)-1} test records")
            print(f"   - Multiple output formats: PNG, JPG, GIF, MP3")
            print(f"   - Multiple AI models: OpenAI, Claude")
            print(f"   - Various priority levels")
        else:
            print("❌ Failed to write test data")
            return False
        
        # Show summary
        print(f"\n📋 Test Data Summary:")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Input Sheet: {input_sheet}")
        print(f"   🔗 View: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Use Google Sheets component to read from '{input_sheet}'")
        print(f"   2. Connect to AI Processing component")
        print(f"   3. Connect to Google Sheets Write component (results will go to 'Results' tab)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_workflow_config():
    """Create sample workflow configuration"""
    print(f"\n🔧 Sample Workflow Configuration")
    print("="*40)
    
    workflow_config = {
        "workflow_name": "AI Asset Generation Pipeline",
        "description": "Read input from Google Sheets, process with AI, write results back",
        
        "components": [
            {
                "type": "manual_trigger",
                "name": "Start",
                "config": {
                    "trigger_data": {}
                }
            },
            {
                "type": "google_sheets",
                "name": "Read Input Data",
                "config": {
                    "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "sheet_name": "AI_Input_Data",
                    "range": "A1:F100"
                }
            },
            {
                "type": "ai_processing",
                "name": "AI Asset Generation",
                "config": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "prompt": "Based on this input data: {input}\n\nGenerate a detailed asset based on the description and requirements. Consider the output format and create appropriate content.",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            {
                "type": "google_sheets_write",
                "name": "Write Results",
                "config": {
                    "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
                    "sheet_name": "Results",
                    "range": "A1",
                    "mode": "overwrite",
                    "data_format": "auto"
                }
            }
        ],
        
        "connections": [
            {"from": "Start", "to": "Read Input Data"},
            {"from": "Read Input Data", "to": "AI Asset Generation"},
            {"from": "AI Asset Generation", "to": "Write Results"}
        ]
    }
    
    print("🎨 Workflow Components:")
    for i, comp in enumerate(workflow_config["components"], 1):
        print(f"   {i}. {comp['name']} ({comp['type']})")
    
    print(f"\n🔗 Connections:")
    for conn in workflow_config["connections"]:
        print(f"   {conn['from']} → {conn['to']}")
    
    print(f"\n💡 Usage Instructions:")
    print(f"   1. Drag components from sidebar to canvas")
    print(f"   2. Connect them in the order shown above")
    print(f"   3. Configure each component with the config shown")
    print(f"   4. Execute the workflow")
    
    return workflow_config

if __name__ == "__main__":
    print("🚀 AI Asset Generation Workflow Setup")
    print("="*55)
    
    # Create test data
    data_success = create_test_data()
    
    if data_success:
        # Show workflow config
        config = create_sample_workflow_config()
        
        print(f"\n🎉 SETUP COMPLETE!")
        print(f"✅ Test data created in Google Sheets")
        print(f"✅ Workflow configuration ready")
        print(f"🎨 Ready to test AI Asset Generation pipeline!")
        
    else:
        print(f"\n❌ Setup failed. Please check:")
        print(f"   1. Google Sheets credentials")
        print(f"   2. Sheet sharing permissions")
        print(f"   3. Network connectivity")
