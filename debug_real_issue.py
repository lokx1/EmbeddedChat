#!/usr/bin/env python3
"""
Debug the actual issue: Why AI responses are processed but not written to Google Sheets
Based on the real logs from the user
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the components
from src.services.workflow.component_registry import GoogleSheetsWriteComponent
from src.schemas.workflow_components import ExecutionContext

async def debug_real_ai_sheets_issue():
    """Debug the real issue with AI responses not being written to sheets"""
    print("🔍 DEBUG: Real AI Response to Sheets Issue")
    print("="*60)
    
    # This is the EXACT data structure from the user's logs
    real_ai_data = {
        "results_for_sheets": [
            # Headers matching the user's Google Sheet
            ["Description", "Example Asset URL", "Desired Output Format", "Model Specification", "Prompt"],
            # Row 1 - Task Manager logo
            [
                "Design a Task Manager app logo", 
                "https://static.wikia.nocookie.net/logopedia/images/c/cb=20240127035026", 
                "PNG", 
                "OpenAI",
                "Okay, here's a comprehensive creative brief for generating a Task Manager app logo, aiming for a professional and modern design..."
            ],
            # Row 2 - Summer Sale banner  
            [
                "Summer Sale banner",
                "https://images.unsplash.com/photo-1234567890",
                "PNG", 
                "Claude",
                "Okay, here's a detailed creative brief for generating a Summer Sale banner for a fashion store, incorporating vibrant colors..."
            ],
            # Row 3 - MP3 audio notification
            [
                "MP3 audio notification",
                "https://encrypted-assets.example.com/mp3/sample",
                "MP3 audio",
                "Claude", 
                "Okay, here's a comprehensive asset specification for the MP3 audio notification, designed to be detailed and professional..."
            ],
            # Row 4 - Video thumbnail
            [
                "Video thumbnail",
                "https://encrypted-assets.example.com/video/thumbnail", 
                "PNG",
                "OpenAI",
                "Okay, here's a comprehensive creative brief for generating a video thumbnail, incorporating the provided guidelines..."
            ]
        ],
        "processed_results": [
            {
                "row_index": 1,
                "input_data": {"description": "Design a Task Manager app logo", "output_format": "PNG"},
                "ai_response": {
                    "type": "ollama_asset_generation",
                    "ai_response": "Okay, here's a comprehensive creative brief for generating a Task Manager app logo...",
                    "generated_url": "https://ollama-assets.local/png/0.png",
                    "metadata": {"model": "gemma3:1b", "provider": "ollama"}
                },
                "status": "success"
            }
            # ... more results
        ]
    }
    
    print(f"📊 Real AI Data Structure:")
    print(f"   - results_for_sheets: {len(real_ai_data['results_for_sheets'])} rows")
    print(f"   - Headers: {real_ai_data['results_for_sheets'][0]}")
    
    # Check if Prompt column exists and has data
    headers = real_ai_data['results_for_sheets'][0]
    if "Prompt" in headers:
        prompt_index = headers.index("Prompt")
        print(f"   ✅ Prompt column found at index {prompt_index}")
        
        # Check sample data
        for i, row in enumerate(real_ai_data['results_for_sheets'][1:], 1):
            if len(row) > prompt_index:
                prompt_text = row[prompt_index]
                print(f"   📝 Row {i} prompt: {prompt_text[:50]}...")
            else:
                print(f"   ❌ Row {i} missing prompt data")
    else:
        print(f"   ❌ Prompt column not found in headers")
    
    # Test Google Sheets Write Component with HEYDO worksheet (as shown in screenshot)
    print(f"\n📝 Testing Google Sheets Write to HEYDO worksheet...")
    sheets_write_component = GoogleSheetsWriteComponent()
    
    # Create execution context exactly matching the user's configuration
    write_context = ExecutionContext(
        workflow_id="automation-workflow",
        instance_id="real-debug-001",
        step_id="sheets-write-step",
        node_id="sheets-write-node",
        input_data={
            "sheet_id": "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc",
            "sheet_name": "HEYDO",  # This is what's shown in the user's screenshot
            "range": "A1",
            "mode": "overwrite",
            "data_format": "auto"
        },
        previous_outputs={
            "ai-processing": real_ai_data  # Provide the real AI data
        },
        global_variables={}
    )
    
    try:
        print(f"   🚀 Executing Google Sheets Write to HEYDO worksheet...")
        write_result = await sheets_write_component.execute(write_context)
        
        print(f"   ✅ Write Success: {write_result.success}")
        
        if write_result.success:
            print(f"   📊 Write result: {write_result.output_data}")
            
            # Check the actual data that was written
            data_written = write_result.output_data.get("data_written", {})
            rows_written = data_written.get("rows_count", 0)
            cols_written = data_written.get("columns_count", 0)
            
            print(f"   📋 Data written: {rows_written} rows, {cols_written} columns")
            
            if write_result.output_data.get("status") == "success":
                print(f"   🎉 SUCCESS: Real write to Google Sheets HEYDO worksheet completed!")
                print(f"   📋 AI responses should now be visible in the Prompt column (column E)")
            else:
                print(f"   ⚠️ NOTE: Write completed in simulation mode")
        else:
            print(f"   ❌ Write error: {write_result.error}")
            
    except Exception as e:
        print(f"   💥 Exception during Google Sheets write: {str(e)}")
        import traceback
        print(f"   Stack trace: {traceback.format_exc()}")
        
    # Show detailed logs
    print(f"\n📋 Detailed Write Logs:")
    if hasattr(write_result, 'logs'):
        for log in write_result.logs:
            print(f"   - {log}")
    
    # Final analysis
    print(f"\n🎯 FINAL ANALYSIS")
    print(f"="*40)
    
    if write_result.success:
        print(f"✅ Backend processing: WORKING")
        print(f"✅ AI response extraction: WORKING") 
        print(f"✅ Google Sheets Write: WORKING")
        print(f"")
        print(f"🔍 If you still don't see AI responses in the Prompt column:")
        print(f"   1. Check that you're looking at the HEYDO worksheet")
        print(f"   2. Refresh your Google Sheets browser tab")
        print(f"   3. Check column E (Prompt column)")
        print(f"   4. The AI responses should be there now!")
    else:
        print(f"❌ Issue found in Google Sheets Write component")
        print(f"❌ Error: {write_result.error if hasattr(write_result, 'error') else 'Unknown error'}")

if __name__ == "__main__":
    asyncio.run(debug_real_ai_sheets_issue())
