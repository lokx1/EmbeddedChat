#!/usr/bin/env python3
"""
Test script for EmailSenderComponent
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_email_component():
    print("🧪 Testing EmailSenderComponent...")
    
    try:
        # Import required modules
        from services.workflow.component_registry import component_registry, ExecutionContext
        from core.config import settings
        
        print(f"✅ Successfully imported modules")
        print(f"📧 Email config loaded: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        
        # Get EmailSenderComponent
        email_component = component_registry.get_component("email")
        if not email_component:
            print("❌ EmailSenderComponent not found in registry")
            return
        
        print(f"✅ Found EmailSenderComponent: {email_component.__class__.__name__}")
        
        # Create test execution context
        context = ExecutionContext(
            input_data={
                "to_email": "your-email@gmail.com",  # Replace with your email
                "subject": "🧪 Test Email from Workflow - {timestamp}",
                "body": """
                <h2>🚀 Workflow Email Test</h2>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p><strong>Test Data:</strong></p>
                <pre>{result}</pre>
                <p>This is a test email from the automated EmailSenderComponent.</p>
                """,
                "email_type": "html",
                "include_attachments": True,
                "from_name": "Workflow System"
            },
            previous_outputs={
                "step1": {"message": "Hello from step 1", "value": 42},
                "step2": {"status": "completed", "items": ["item1", "item2", "item3"]},
                "analysis": {"success_rate": 95.5, "errors": 2, "total": 100}
            },
            workflow_name="Test Email Workflow",
            instance_id="test-123"
        )
        
        print("📝 Created test execution context")
        print(f"   Recipient: {context.input_data['to_email']}")
        print(f"   Subject template: {context.input_data['subject']}")
        
        # Execute email component
        print("\n📤 Executing EmailSenderComponent...")
        result = await email_component.execute(context)
        
        # Display results
        print(f"\n📊 Execution Results:")
        print(f"   Success: {result.success}")
        print(f"   Execution time: {result.execution_time_ms}ms")
        
        if result.success:
            print(f"   ✅ Output data: {result.output_data}")
            print(f"   📝 Logs: {result.logs}")
            print(f"   ➡️  Next steps: {result.next_steps}")
            print(f"\n🎉 Email sent successfully!")
        else:
            print(f"   ❌ Error: {result.error}")
            print(f"   📝 Logs: {result.logs}")
            print(f"   ➡️  Next steps: {result.next_steps}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure backend dependencies are installed")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 EmailSenderComponent Test")
    print("=" * 50)
    
    # Run test
    asyncio.run(test_email_component())
