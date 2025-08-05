#!/usr/bin/env python3
"""
Simple test để gửi email report trực tiếp qua EmailReportComponent
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

async def test_direct_email_component():
    print("🧪 TESTING EMAIL REPORT COMPONENT DIRECTLY")
    print("=" * 60)
    
    try:
        # Import components
        from services.workflow.component_registry import EmailReportComponent
        from schemas.workflow_components import ExecutionContext
        from datetime import datetime
        
        # Create execution context
        context = ExecutionContext(
            workflow_id="test-workflow-123",
            instance_id="test-instance-456",
            execution_id="test-execution-789",
            current_step="test_email_step",
            input_data={},
            node_outputs={},
            global_variables={}
        )
        
        # Create component
        component = EmailReportComponent()
        
        # Test parameters
        params = {
            "recipient_email": "vuducanhhn@gmail.com",
            "report_title": "Direct Test Report",
            "include_charts": True,
            "report_type": "execution"
        }
        
        print("1️⃣ Executing EmailReportComponent directly...")
        print(f"   Context: workflow_id={context.workflow_id}")
        print(f"   Params: {params}")
        
        # Execute component
        result = await component.execute(context, params)
        
        print("✅ Component executed successfully!")
        print(f"📧 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_email_component())
