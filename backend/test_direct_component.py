#!/usr/bin/env python3
"""Test GoogleSheetsWriteComponent directly with Test sheet"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.workflow.component_registry import GoogleSheetsWriteComponent
from datetime import datetime

def main():
    print("🧪 Testing GoogleSheetsWriteComponent directly with Test sheet")
    
    # Create component
    component = GoogleSheetsWriteComponent()
    
    # Test data
    test_data = {
        "test_user": "Direct Test User",
        "age": 35,
        "city": "Test City Direct",
        "timestamp": datetime.now().isoformat()
    }
    
    # Configuration for Test sheet
    config = {
        "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
        "sheet_name": "Test",  # This should trigger auto-create
        "range": "A2",
        "mode": "append",
        "data_format": "auto"
    }
    
    print(f"📊 Test data: {test_data}")
    print(f"⚙️  Config: {config}")
    
    # Execute component
    print("\n🔄 Executing GoogleSheetsWriteComponent...")
    
    try:
        result = component.execute(test_data, config)
        print(f"✅ Component execution result: {result}")
        
        if result.get('success'):
            print("✅ Write operation successful!")
            
            # Wait and check sheet
            import time
            time.sleep(3)
            
            # Check Test sheet data
            from services.google_sheets_service import GoogleSheetsService
            service = GoogleSheetsService()
            if service.authenticate():
                data = service.read_sheet(config["sheet_id"], "Test!A1:D10")
                print(f'\n📊 Data in Test sheet after write ({len(data) if data else 0} rows):')
                if data:
                    for i, row in enumerate(data):
                        print(f'  Row {i+1}: {row}')
                else:
                    print("  No data found")
            else:
                print("❌ Failed to authenticate for verification")
        else:
            print(f"❌ Write operation failed: {result}")
            
    except Exception as e:
        print(f"❌ Error executing component: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
