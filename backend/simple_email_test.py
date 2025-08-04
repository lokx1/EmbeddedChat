#!/usr/bin/env python3
"""
Simple test for EmailSenderComponent
"""
import asyncio
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

async def main():
    print("🧪 Testing EmailSenderComponent...")
    
    try:
        # Import with absolute imports
        import services.workflow.component_registry as registry
        import core.config as config
        
        print("✅ Modules imported successfully")
        
        # Get settings
        settings = config.settings
        print(f"📧 SMTP Server: {settings.SMTP_SERVER}")
        print(f"📧 SMTP Port: {settings.SMTP_PORT}")
        print(f"📧 From Email: {settings.SMTP_FROM_EMAIL}")
        
        # Get component registry
        comp_registry = registry.component_registry
        print(f"📦 Available components: {list(comp_registry.components.keys())}")
        
        # Get EmailSenderComponent
        email_comp = comp_registry.get_component("email")
        if email_comp:
            print(f"✅ EmailSenderComponent found: {email_comp.__class__.__name__}")
            
            # Create simple test context
            class TestContext:
                def __init__(self):
                    self.input_data = {
                        "to_email": "your-email@gmail.com",  # Replace with your email  
                        "subject": "Test Email - {timestamp}",
                        "body": "Hello from EmailSenderComponent!\n\nTest data: {result}",
                        "email_type": "text"
                    }
                    self.previous_outputs = {
                        "test": "data",
                        "value": 123
                    }
                    self.workflow_name = "Test Workflow"
                    self.instance_id = "test-123"
            
            context = TestContext()
            print(f"📝 Test context created")
            
            # Execute component
            print("📤 Sending test email...")
            result = await email_comp.execute(context)
            
            print(f"📊 Result:")
            print(f"   Success: {result.success}")
            print(f"   Time: {result.execution_time_ms}ms")
            
            if result.success:
                print(f"   ✅ Data: {result.output_data}")
                print(f"   📝 Logs: {result.logs}")
            else:
                print(f"   ❌ Error: {result.error}")
                print(f"   📝 Logs: {result.logs}")
                
        else:
            print("❌ EmailSenderComponent not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
