#!/usr/bin/env python3
"""
Test AI Processing Component with Google Sheets Integration
"""

from src.services.workflow.component_registry import GoogleSheetsComponent, AIProcessingComponent, GoogleSheetsWriteComponent, ExecutionContext
from src.services.google_sheets_service import GoogleSheetsService
import asyncio
from datetime import datetime

async def test_ai_processing_pipeline():
    """Test the complete AI processing pipeline"""
    print("🧪 Testing AI Processing Pipeline")
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
            workflow_id="test-ai-pipeline",
            instance_id="test-instance-ai",
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
        print(f"📋 Columns: {', '.join(sheets_result.output_data.get('spreadsheet_info', {}).get('columns', []))}")
        
        # Step 2: Process with AI
        print(f"\n🤖 Step 2: Processing with AI...")
        
        ai_component = AIProcessingComponent()
        ai_context = ExecutionContext(
            workflow_id="test-ai-pipeline",
            instance_id="test-instance-ai",
            step_id="step-2-ai",
            input_data={
                "provider": "openai",
                "model": "gpt-4o",
                "prompt": "Based on this asset request: {input}\n\nGenerate a detailed description for creating this asset. Include technical specifications, style guidelines, and implementation notes.",
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
        print(f"⏱️  Processing time: {summary.get('processing_time_ms', 0)}ms")
        print(f"🤖 Provider: {summary.get('provider')} ({summary.get('model')})")
        
        # Show some sample results
        results = ai_result.output_data.get('processed_results', [])[:3]
        print(f"\n📋 Sample Results:")
        for i, result in enumerate(results, 1):
            input_desc = result.get('input_data', {}).get('description', 'No description')
            ai_response = result.get('ai_response', {})
            status = result.get('status', 'unknown')
            print(f"   {i}. {input_desc[:50]}... → {status}")
            if ai_response and 'generated_url' in ai_response:
                print(f"      Generated: {ai_response['generated_url']}")
        
        # Step 3: Write results to Google Sheets
        print(f"\n📝 Step 3: Writing results to Google Sheets...")
        
        write_component = GoogleSheetsWriteComponent()
        
        # Use the pre-formatted results
        results_data = ai_result.output_data.get('results_for_sheets', [])
        
        write_context = ExecutionContext(
            workflow_id="test-ai-pipeline",
            instance_id="test-instance-ai",
            step_id="step-3-write",
            input_data={
                "sheet_id": sheet_id,
                "sheet_name": output_sheet,
                "range": "A1",
                "mode": "overwrite",
                "data_format": "auto",
                "data": results_data
            },
            previous_outputs={
                "step-1-read": sheets_result.output_data,
                "step-2-ai": ai_result.output_data
            },
            global_variables={}
        )
        
        write_result = await write_component.execute(write_context)
        
        if not write_result.success:
            print(f"❌ Failed to write results: {write_result.error}")
            return False
        
        print(f"✅ Successfully wrote results to '{output_sheet}' sheet!")
        print(f"📊 Wrote {len(results_data)} rows")
        
        # Step 4: Show final summary
        print(f"\n🎉 Pipeline Execution Summary:")
        print("="*40)
        print(f"✅ Input data read: {len(sheets_result.output_data.get('records', []))} records")
        print(f"✅ AI processing: {summary.get('successful_records', 0)} successful")
        print(f"✅ Results written: {len(results_data)} rows")
        print(f"⏱️  Total time: {sheets_result.execution_time_ms + ai_result.execution_time_ms + write_result.execution_time_ms}ms")
        
        print(f"\n🔗 View Results:")
        print(f"   Input:  https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0 ('{input_sheet}' tab)")
        print(f"   Output: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=1 ('{output_sheet}' tab)")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_components():
    """Test individual AI processing methods"""
    print(f"\n🔧 Testing Individual AI Processing Methods")
    print("="*45)
    
    ai_component = AIProcessingComponent()
    
    # Test record
    test_record = {
        "description": "Beautiful sunset landscape",
        "output_format": "PNG",
        "ai_model": "OpenAI",
        "priority": "High"
    }
    
    # Test different providers
    providers = [
        ("openai", "gpt-4o"),
        ("claude", "claude-3-5-sonnet"),
        ("ollama", "llama3.2")
    ]
    
    for provider, model in providers:
        print(f"\n🤖 Testing {provider} ({model})...")
        
        try:
            result = await ai_component._process_with_ai(
                provider=provider,
                model=model,
                prompt="Generate an asset based on: " + str(test_record),
                temperature=0.7,
                max_tokens=500,
                record=test_record
            )
            
            print(f"✅ {provider.upper()} Success:")
            print(f"   Type: {result.get('type', 'unknown')}")
            print(f"   URL: {result.get('generated_url', 'N/A')}")
            print(f"   Quality: {result.get('metadata', {}).get('quality', 'N/A')}")
            print(f"   Processing time: {result.get('metadata', {}).get('processing_time', 'N/A')}")
            
        except Exception as e:
            print(f"❌ {provider.upper()} Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 AI Processing Component Test Suite")
    print("="*55)
    
    async def run_tests():
        # Test 1: Individual components
        await test_individual_components()
        
        # Test 2: Full pipeline
        pipeline_success = await test_ai_processing_pipeline()
        
        if pipeline_success:
            print(f"\n🎯 ALL TESTS PASSED!")
            print(f"✅ AI Processing component is working")
            print(f"✅ Google Sheets integration is working")
            print(f"✅ Pipeline execution is successful")
            print(f"🎨 Ready for frontend testing!")
        else:
            print(f"\n⚠️  Some tests failed")
            print(f"💡 Check component configurations and API access")
    
    # Run async tests
    asyncio.run(run_tests())
