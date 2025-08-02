#!/usr/bin/env python3
"""
Quick test with timeout for Google Sheets
"""
import sys
import os
import signal
from datetime import datetime

# Add timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

# Set timeout (10 seconds)
signal.signal(signal.SIGALRM, timeout_handler)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.services.google_sheets_service import get_sheets_service
    
    print("=== Quick Google Sheets Test ===")
    
    # Start timeout
    signal.alarm(10)
    
    # Create service and authenticate
    sheets_service = get_sheets_service()
    print("✓ Service created")
    
    auth_result = sheets_service.authenticate()
    print(f"✓ Authentication: {auth_result}")
    
    if auth_result:
        # Test write with timeout
        sheet_id = "1QH86P8_g1v7iDTrV5aZrxwl-MdOQJgdC6H4I8xKVaZw"
        range_name = "Result_Test!B35"
        test_data = [["Timeout Test", datetime.now().strftime("%H:%M:%S")]]
        
        print(f"✓ Writing to {range_name}...")
        write_result = sheets_service.write_sheet(sheet_id, range_name, test_data)
        print(f"✓ Write result: {write_result}")
        
        if write_result:
            print("✅ SUCCESS!")
        else:
            print("❌ WRITE FAILED!")
    else:
        print("❌ AUTH FAILED!")
        
    # Cancel timeout
    signal.alarm(0)
        
except TimeoutError:
    print("❌ TIMEOUT: Operation took too long!")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    signal.alarm(0)
