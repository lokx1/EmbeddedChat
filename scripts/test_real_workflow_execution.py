#!/usr/bin/env python3
"""
Direct test of AI Processing Pipeline with real Google Sheets writes
"""

from src.services.workflow.component_registry import GoogleSheetsComponent, AIProcessingComponent, GoogleSheetsWriteComponent, ExecutionContext
from src.services.google_sheets_service import GoogleSheetsService
import asyncio
from datetime import datetime

async def test_real_workflow_execution():
    """Test the complete workflow with real Google Sheets writes"""
    print("🧪 Testing REAL AI Processing Pipeline")
    print("="*50)
    
    # Test data
    sheet_id = '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc'
    input_sheet = 'AI_Input_Data'
    output_sheet = 'Results'
    
    try:
        # Step 1: Read from Google Sheets
        print("📊 Step 1: Reading input data from Google Sheets...")
        
        sheets_component = GoogleSheetsComponent()
        sheets_context = ExecutionContext(
            workflow_id="real-test-pipeline",
            instance_id="real-test-instance",
            step_id="step-1-read",
            input_data={
                "sheet_id": sheet_id,
                "sheet_name": input_sheet,
                "range": "A1:F100"
            },
            previous_outputs={},
            global_variables={}
        )
        
        sheets_result = await sheets_component.execute(sheets_context)
        
        if not sheets_result.success:
            print(f"❌ Failed to read Google Sheets: {sheets_result.error}")
            return False
        
        print(f"✅ Successfully read {len(sheets_result.output_data.get('records', []))} records")
        
        # Show input data
        records = sheets_result.output_data.get('records', [])
        print(f"📋 Input Records:")
        for i, record in enumerate(records[:3], 1):
            description = record.get('description', 'No description')
            output_format = record.get('output_format', 'Unknown')
            print(f"   {i}. {description[:50]}... → {output_format}")
        
        # Step 2: Process with AI
        print(f"\n🤖 Step 2: Processing with AI...")
        
        ai_component = AIProcessingComponent()
        ai_context = ExecutionContext(
            workflow_id="real-test-pipeline",
            instance_id="real-test-instance",
            step_id="step-2-ai",
            input_data={
                "provider": "openai",
                "model": "gpt-4o",
                "prompt": "Based on this asset request: {input}\n\nGenerate a comprehensive asset specification including technical details, style guidelines, and implementation notes.",
                "temperature": 0.7,
                "max_tokens": 500
            },
            previous_outputs={
                "step-1-read": sheets_result.output_data
            },
            global_variables={}
        )
        
        ai_result = await ai_component.execute(ai_context)
        
        if not ai_result.success:
            print(f"❌ AI processing failed: {ai_result.error}")
            return False
        
        print(f"✅ AI processing completed!")
        summary = ai_result.output_data.get('summary', {})
        print(f"📊 Processed: {summary.get('successful_records', 0)}/{summary.get('total_records', 0)} records")
        
        # Show processed results
        results = ai_result.output_data.get('processed_results', [])
        print(f"📋 AI Results:")
        for i, result in enumerate(results[:3], 1):
            input_desc = result.get('input_data', {}).get('description', 'No description')
            ai_response = result.get('ai_response', {})
            status = result.get('status', 'unknown')
            generated_url = ai_response.get('generated_url', 'No URL') if ai_response else 'No URL'
            print(f"   {i}. {input_desc[:40]}... → {status}")
            print(f"      Generated: {generated_url}")
        
        # Step 3: Write results to Google Sheets using REAL API
        print(f"\n📝 Step 3: Writing results to Google Sheets (REAL WRITE)...")
        
        # Get formatted results for sheets
        results_data = ai_result.output_data.get('results_for_sheets', [])
        
        if not results_data:
            print("❌ No results data to write")
            return False
        
        print(f"📊 Data to write: {len(results_data)} rows, {len(results_data[0]) if results_data else 0} columns")
        
        # Use GoogleSheetsService directly for guaranteed write
        print("🔧 Using GoogleSheetsService directly...")
        service = GoogleSheetsService()
        
        if not service.authenticate():
            print("❌ Failed to authenticate with Google Sheets")
            return False
        
        print("✅ Authentication successful")
        
        # Ensure Results sheet exists
        info = service.get_sheet_info(sheet_id)
        if info:
            sheet_exists = any(s['title'] == output_sheet for s in info['sheets'])
            if not sheet_exists:
                print(f"⚠️  Creating '{output_sheet}' sheet...")
                if not service.create_sheet(sheet_id, output_sheet):
                    print(f"❌ Failed to create '{output_sheet}' sheet")
                    return False
        
        # Clear existing data first
        print("🧹 Clearing existing data...")
        clear_success = service.clear_sheet(sheet_id, f"{output_sheet}!A1:Z1000")
        if clear_success:
            print("✅ Existing data cleared")
        
        # Write new data
        print("✍️  Writing new results...")
        range_name = f"{output_sheet}!A1"
        write_success = service.write_sheet(sheet_id, range_name, results_data)
        
        if write_success:
            print(f"✅ Successfully wrote {len(results_data)} rows to '{output_sheet}' sheet!")
            
            # Verify write by reading back
            print("🔍 Verifying write by reading back...")
            verify_data = service.read_sheet(sheet_id, f"{output_sheet}!A1:L{len(results_data)+2}")
            
            if verify_data:
                print(f"✅ Verification successful: Read back {len(verify_data)} rows")
                print(f"📋 First few rows:")
                for i, row in enumerate(verify_data[:3], 1):
                    print(f"   Row {i}: {row[:4]}...")  # Show first 4 columns
            else:
                print("⚠️  Verification failed: Could not read back data")
        else:
            print("❌ Failed to write results to sheet")
            return False
        
        # Final summary
        print(f"\n🎉 REAL WORKFLOW EXECUTION COMPLETE!")
        print("="*45)
        print(f"✅ Input: Read {len(records)} records from '{input_sheet}'")
        print(f"✅ AI: Processed {summary.get('successful_records', 0)} records successfully")
        print(f"✅ Output: Wrote {len(results_data)} rows to '{output_sheet}'")
        print(f"⏱️  Total time: {sheets_result.execution_time_ms + ai_result.execution_time_ms}ms")
        
        print(f"\n🔗 View Results:")
        print(f"   Input:  https://docs.google.com/spreadsheets/d/{sheet_id}/edit ('{input_sheet}' tab)")
        print(f"   Output: https://docs.google.com/spreadsheets/d/{sheet_id}/edit ('{output_sheet}' tab)")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow execution error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def quick_verify_sheets():
    """Quick verification of Google Sheets content"""
    print(f"\n🔍 Quick Verification of Google Sheets")
    print("="*40)
    
    sheet_id = '1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc'
    
    service = GoogleSheetsService()
    if not service.authenticate():
        print("❌ Authentication failed")
        return
    
    # Check input data
    print("📊 Checking input data...")
    input_data = service.read_sheet(sheet_id, "AI_Input_Data!A1:F10")
    if input_data:
        print(f"✅ Input sheet has {len(input_data)} rows")
        print(f"   Headers: {input_data[0] if input_data else 'No headers'}")
    else:
        print("❌ No input data found")
    
    # Check results data
    print("📝 Checking results data...")
    results_data = service.read_sheet(sheet_id, "Results!A1:L10")
    if results_data:
        print(f"✅ Results sheet has {len(results_data)} rows")
        print(f"   Headers: {results_data[0] if results_data else 'No headers'}")
        if len(results_data) > 1:
            print(f"   Sample data: {results_data[1][:4]}...")
    else:
        print("❌ No results data found")

if __name__ == "__main__":
    print("🚀 REAL AI Processing Pipeline Test")
    print("="*55)
    
    async def run_real_test():
        # First verify current state
        await quick_verify_sheets()
        
        # Run real workflow
        success = await test_real_workflow_execution()
        
        if success:
            print(f"\n🎯 REAL TEST PASSED!")
            print(f"✅ Data has been written to Google Sheets")
            print(f"✅ Pipeline is working correctly")
            
            # Verify again
            await quick_verify_sheets()
        else:
            print(f"\n❌ Real test failed")
    
    # Run the real test
    asyncio.run(run_real_test())
