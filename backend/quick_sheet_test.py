#!/usr/bin/env python3
"""
Simple test to verify sheet access after fix
"""
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def quick_test():
    """Quick test of sheet access"""
    
    try:
        from src.services.google_sheets_service import get_sheets_service
        
        print("🧪 Quick Sheet Access Test")
        print("=" * 30)
        
        sheets_service = get_sheets_service()
        if sheets_service.authenticate():
            sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
            
            # Test both sheet names
            for sheet_name in ["Test", "Result_Test"]:
                try:
                    print(f"Testing {sheet_name}...")
                    # Try simple read
                    data = sheets_service.read_sheet(sheet_id, f"{sheet_name}!A1:A1")
                    print(f"✅ {sheet_name}: Accessible")
                    
                    # Try simple write
                    test_write = sheets_service.write_sheet(
                        sheet_id, 
                        f"{sheet_name}!A10", 
                        [["Quick Test", time.strftime("%H:%M:%S")]]
                    )
                    if test_write:
                        print(f"✅ {sheet_name}: Write successful")
                    else:
                        print(f"❌ {sheet_name}: Write failed")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "Unable to parse range" in error_msg:
                        print(f"❌ {sheet_name}: Sheet does NOT exist")
                    else:
                        print(f"❌ {sheet_name}: {error_msg[:50]}...")
                        
            print(f"\n💡 After creating 'Test' sheet, run frontend workflow again!")
            
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    quick_test()
