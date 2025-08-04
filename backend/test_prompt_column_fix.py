#!/usr/bin/env python3
"""
Test the complete workflow after fixing AI response formatting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import json
from src.services.workflow.workflow_engine import WorkflowEngine
from src.services.workflow.models import WorkflowInstance, WorkflowInstanceCreate, WorkflowInstanceStatus
from src.database.connection import get_database

async def test_workflow_with_prompt_column():
    print("🚀 Testing workflow with Prompt column fix...")
    
    # Load the workflow configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'workflow_config_test_new.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        workflow_config = json.load(f)
    
    print(f"📋 Workflow: {workflow_config['name']}")
    print(f"📋 Steps: {len(workflow_config['steps'])}")
    
    # Connect to database
    database = get_database()
    
    # Create workflow instance
    workflow_create = WorkflowInstanceCreate(
        name=f"Test Prompt Column Fix",
        description="Testing AI response in Prompt column after fix",
        config=workflow_config,
        status=WorkflowInstanceStatus.PENDING
    )
    
    workflow_instance = WorkflowInstance(
        id=999,  # Test ID
        **workflow_create.dict()
    )
    
    # Execute workflow
    engine = WorkflowEngine(database)
    print(f"\n🔄 Executing workflow...")
    
    result = await engine.execute_workflow(workflow_instance)
    
    print(f"\n✅ Execution completed!")
    print(f"📊 Status: {result.status}")
    print(f"⏱️ Duration: {result.execution_time_ms}ms")
    
    if result.error:
        print(f"❌ Error: {result.error}")
    
    # Print step results
    for i, step_result in enumerate(result.step_results):
        print(f"\n📝 Step {i+1}: {step_result.step_name}")
        print(f"   ✅ Success: {step_result.success}")
        if step_result.error:
            print(f"   ❌ Error: {step_result.error}")
        
        # Check if this is AI Processing step with results_for_sheets
        if "AI Processing" in step_result.step_name and step_result.output_data:
            if "results_for_sheets" in step_result.output_data:
                results = step_result.output_data["results_for_sheets"]
                print(f"   📊 results_for_sheets structure: {len(results)} rows")
                if len(results) > 0:
                    print(f"   📊 Headers: {results[0]}")
                    if len(results) > 1:
                        print(f"   📊 First data row: {results[1]}")
                        # Check if Prompt column has content
                        headers = results[0]
                        if "Prompt" in headers:
                            prompt_index = headers.index("Prompt")
                            first_row = results[1]
                            if len(first_row) > prompt_index:
                                prompt_content = first_row[prompt_index]
                                print(f"   🎯 Prompt column content: '{prompt_content[:100]}...' (length: {len(prompt_content)})")
                                if prompt_content and len(prompt_content) > 10:
                                    print(f"   ✅ SUCCESS: Prompt column has content!")
                                else:
                                    print(f"   ❌ FAIL: Prompt column is empty or too short")
    
    print(f"\n🎯 Check your Google Sheet now - the Prompt column should be populated!")
    return result

if __name__ == "__main__":
    asyncio.run(test_workflow_with_prompt_column())
