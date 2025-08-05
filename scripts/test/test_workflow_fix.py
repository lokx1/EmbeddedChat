#!/usr/bin/env python3
"""
Quick Fix Test for Workflow Issues
"""
import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, src_dir)

def test_imports():
    """Test if we can import the required components"""
    print("🔧 TESTING IMPORTS")
    print("="*50)
    
    try:
        from backend.src.services.workflow.component_registry import (
            GoogleSheetsComponent, 
            AIProcessingComponent, 
            GoogleSheetsWriteComponent,
            GoogleDriveWriteComponent
        )
        print("✅ All workflow components imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_conversion():
    """Test CSV conversion logic"""
    print("\n📋 TESTING CSV CONVERSION")
    print("="*50)
    
    try:
        from backend.src.services.workflow.component_registry import GoogleDriveWriteComponent
        
        # Sample AI processing data
        ai_data = {
            "processed_results": [
                {
                    "row_index": 1,
                    "input_data": {"description": "Logo design", "output_format": "PNG"},
                    "ai_response": {"generated_url": "https://ollama-assets.local/png/1234.png"},
                    "status": "success"
                }
            ],
            "results_for_sheets": [
                ["Row Index", "Description", "Format", "Status", "URL"],
                [1, "Logo design", "PNG", "success", "https://ollama-assets.local/png/1234.png"]
            ]
        }
        
        # Test CSV conversion
        drive_component = GoogleDriveWriteComponent()
        csv_content = drive_component._prepare_file_content(ai_data, "csv")
        csv_text = csv_content.decode('utf-8')
        
        print("📄 CSV Content Preview:")
        print("-" * 40)
        print(csv_text)
        print("-" * 40)
        
        # Check if CSV content looks correct
        lines = csv_text.strip().split('\n')
        if len(lines) >= 2 and 'Row Index' in lines[0]:
            print("✅ CSV conversion working correctly")
            return True
        else:
            print("❌ CSV conversion format issue")
            return False
            
    except Exception as e:
        print(f"❌ CSV conversion error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 WORKFLOW FIX VERIFICATION")
    print("="*70)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed - stopping here")
        return
    
    # Test 2: CSV conversion
    if not test_csv_conversion():
        print("\n❌ CSV conversion test failed")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("\n📋 VERIFICATION RESULTS:")
    print("✅ Component imports working")
    print("✅ CSV conversion working")
    print("✅ AI data format supported")
    
    print("\n🎯 NEXT STEPS TO FIX YOUR WORKFLOW:")
    print("1. Add Google Sheets Write component to your workflow")
    print("2. Connect AI Processing → Google Sheets Write")
    print("3. Set Google Drive Write file_type to 'csv'")
    print("4. Test the complete workflow")
    
    print("\n📝 WORKFLOW CONFIGURATION:")
    print("   Sheets Read → AI Processing → [Sheets Write + Drive Write]")
    print("                                      ↓              ↓")
    print("                                  New Sheet     CSV File")

if __name__ == "__main__":
    main()
