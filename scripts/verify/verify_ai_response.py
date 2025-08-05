#!/usr/bin/env python3
"""
Verify AI Response in Google Sheets
Check if Prompt column with AI responses is written to Google Sheets
"""

import sys
import os
import asyncio

# Add backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.workflow.google_services import GoogleSheetsService

async def verify_ai_response_in_sheets():
    print("🔍 VERIFYING AI RESPONSE IN GOOGLE SHEETS")
    print("="*50)
    
    try:
        # Use correct credentials path
        credentials_path = os.path.join(os.path.dirname(__file__), 'backend', 'credentials.json')
        service = GoogleSheetsService(credentials_path)
        
        if await service.authenticate():
            print("✅ Google Sheets authenticated")
            
            # Check the test sheet
            sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
            sheet_name = "Direct_AI_Test"
            
            print(f"📊 Reading from sheet: {sheet_name}")
            
            # Read data from the test sheet
            success, result = await service.read_sheet(sheet_id, sheet_name, "A1:M10")
            
            if success and result.get('operation') == 'read_success':
                data = result.get('data', {})
                values = data.get('values', [])
                
                print(f"📝 Found {len(values)} rows")
                
                if values:
                    headers = values[0] if len(values) > 0 else []
                    print(f"📋 Headers ({len(headers)} columns):")
                    
                    for i, header in enumerate(headers):
                        marker = "⭐" if header == "Prompt" else "  "
                        print(f"   {marker} {i+1:2d}. {header}")
                    
                    # Check for Prompt column
                    if "Prompt" in headers:
                        prompt_index = headers.index("Prompt")
                        print(f"\n🎯 Prompt column found at index {prompt_index+1} (column {chr(65+prompt_index)})")
                        
                        # Show data rows
                        if len(values) > 1:
                            print(f"\n📝 Data rows:")
                            for i, row in enumerate(values[1:], 1):
                                if len(row) > prompt_index:
                                    description = row[1] if len(row) > 1 else "N/A"
                                    prompt_text = row[prompt_index]
                                    print(f"   Row {i}:")
                                    print(f"      Description: {description}")
                                    print(f"      Prompt: {prompt_text[:100]}{'...' if len(prompt_text) > 100 else ''}")
                                    
                                    # Check if AI response is cleaned (no <think> tags)
                                    if "<think>" in prompt_text or "</think>" in prompt_text:
                                        print(f"      ❌ WARNING: <think> tags found in prompt!")
                                    else:
                                        print(f"      ✅ Prompt is clean (no <think> tags)")
                                    print()
                        else:
                            print(f"❌ No data rows found (only headers)")
                    else:
                        print(f"\n❌ Prompt column not found in headers!")
                        print(f"Available columns: {headers}")
                else:
                    print(f"❌ No data found in sheet")
            else:
                print(f"❌ Failed to read sheet: {result}")
                
                # Try to read from other common sheet names
                for alt_sheet in ["AI_Test_Fixed", "Sheet1", "AI_Results"]:
                    print(f"\n🔍 Trying sheet: {alt_sheet}")
                    success, result = await service.read_sheet(sheet_id, alt_sheet, "A1:M5")
                    if success and result.get('operation') == 'read_success':
                        data = result.get('data', {})
                        values = data.get('values', [])
                        if values:
                            print(f"   ✅ Found {len(values)} rows in {alt_sheet}")
                            if len(values) > 0:
                                headers = values[0]
                                if "Prompt" in headers:
                                    print(f"   ⭐ Prompt column found!")
                                else:
                                    print(f"   📋 Headers: {headers}")
                        else:
                            print(f"   📭 Empty sheet")
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_ai_response_in_sheets())
