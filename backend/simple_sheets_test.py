#!/usr/bin/env python3
"""
Simple test script for Google Sheets API
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.services.google_sheets_service import get_sheets_service
    
    print("=== Testing Google Sheets API directly ===")
    
    # Create service
    sheets_service = get_sheets_service()
    print(f"Service created: {type(sheets_service)}")
    
    # Test authentication
    auth_result = sheets_service.authenticate()
    print(f"Authentication: {auth_result}")
    
    if auth_result:
        # Test write
        sheet_id = "1QH86P8_g1v7iDTrV5aZrxwl-MdOQJgdC6H4I8xKVaZw"
        range_name = "Result_Test!A25"
        test_data = [["Simple Test", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]
        
        print(f"Writing to {range_name}: {test_data}")
        write_result = sheets_service.write_sheet(sheet_id, range_name, test_data)
        print(f"Write result: {write_result}")
        
        if write_result:
            print("✅ SUCCESS: Direct API write worked!")
        else:
            print("❌ FAILED: Direct API write failed!")
    else:
        print("❌ FAILED: Authentication failed!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
