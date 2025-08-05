#!/usr/bin/env python3
"""
Backend Component Fix Checker
Check và fix các components để đảm bảo AI output được process đúng
"""

def check_ai_processing_component():
    """Kiểm tra AI Processing Component có tạo ra results_for_sheets không"""
    print("🔍 CHECKING: AI Processing Component")
    print("="*50)
    
    try:
        with open("backend/src/services/workflow/component_registry.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check key functions
        checks = [
            ("_format_results_for_sheets", "✅ Format results for sheets function found"),
            ("results_for_sheets", "✅ Results for sheets output found"),
            ("processed_results", "✅ Processed results output found")
        ]
        
        all_good = True
        for check, message in checks:
            if check in content:
                print(message)
            else:
                print(f"❌ Missing: {check}")
                all_good = False
        
        if all_good:
            print("✅ AI Processing Component looks good")
        else:
            print("❌ AI Processing Component needs fixes")
            
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking AI Processing Component: {e}")
        return False

def check_sheets_write_component():
    """Kiểm tra Google Sheets Write Component"""
    print("\n🔍 CHECKING: Google Sheets Write Component")
    print("="*55)
    
    try:
        with open("backend/src/services/workflow/component_registry.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for Google Sheets Write component
        if "class GoogleSheetsWriteComponent" in content:
            print("✅ Google Sheets Write Component found")
            
            # Check key methods
            if "_process_input_data" in content:
                print("✅ Input data processing method found")
            else:
                print("❌ Missing input data processing method")
                
            if "_write_to_google_sheets" in content:
                print("✅ Google Sheets write method found")
            else:
                print("❌ Missing Google Sheets write method")
                
            return True
        else:
            print("❌ Google Sheets Write Component not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Google Sheets Write Component: {e}")
        return False

def check_drive_write_component():
    """Kiểm tra Google Drive Write Component"""
    print("\n🔍 CHECKING: Google Drive Write Component")
    print("="*50)
    
    try:
        with open("backend/src/services/workflow/component_registry.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for Google Drive Write component
        if "class GoogleDriveWriteComponent" in content:
            print("✅ Google Drive Write Component found")
            
            # Check CSV handling
            if "results_for_sheets" in content and "_prepare_file_content" in content:
                print("✅ CSV conversion logic found")
            else:
                print("❌ Missing CSV conversion for AI data")
                
            if "text/csv" in content:
                print("✅ CSV MIME type handling found")
            else:
                print("❌ Missing CSV MIME type")
                
            return True
        else:
            print("❌ Google Drive Write Component not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Google Drive Write Component: {e}")
        return False

def check_workflow_execution():
    """Kiểm tra workflow execution engine"""
    print("\n🔍 CHECKING: Workflow Execution Engine")
    print("="*50)
    
    try:
        with open("backend/src/services/workflow/execution_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check execution flow
        if "previous_outputs" in content:
            print("✅ Previous outputs handling found")
        else:
            print("❌ Missing previous outputs handling")
            
        if "_execute_node" in content:
            print("✅ Node execution method found")
        else:
            print("❌ Missing node execution method")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking Workflow Execution Engine: {e}")
        return False

def main():
    """Main checker function"""
    print("🚀 BACKEND COMPONENT FIX CHECKER")
    print("="*70)
    
    # Run all checks
    ai_ok = check_ai_processing_component()
    sheets_ok = check_sheets_write_component()
    drive_ok = check_drive_write_component()
    execution_ok = check_workflow_execution()
    
    print("\n📋 SUMMARY")
    print("="*30)
    
    if ai_ok and sheets_ok and drive_ok and execution_ok:
        print("✅ ALL BACKEND COMPONENTS LOOK GOOD!")
        print("\n🎯 The issue is likely in the FRONTEND WORKFLOW configuration:")
        print("   - Add Google Sheets Write component")
        print("   - Set Google Drive Write file_type to 'csv'")
        print("   - Connect AI Processing to both output components")
        
    else:
        print("❌ SOME BACKEND COMPONENTS NEED ATTENTION:")
        if not ai_ok:
            print("   - AI Processing Component needs fixes")
        if not sheets_ok:
            print("   - Google Sheets Write Component needs fixes")
        if not drive_ok:
            print("   - Google Drive Write Component needs fixes")
        if not execution_ok:
            print("   - Workflow Execution Engine needs fixes")
    
    print("\n📝 NEXT STEPS:")
    print("1. If backend is OK: Fix frontend workflow configuration")
    print("2. If backend needs fixes: Check the component implementations")
    print("3. Test the workflow after making changes")

if __name__ == "__main__":
    main()
