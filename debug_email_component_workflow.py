#!/usr/bin/env python3
"""
Debug script để kiểm tra EmailReportComponent trong workflow execution
"""

import asyncio
import aiohttp
import json
import time

BACKEND_URL = "http://localhost:8000/api/v1"

async def test_email_component_in_workflow():
    print("🚀 TESTING EMAIL REPORT COMPONENT IN WORKFLOW")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Get component registry
        print("1️⃣ Checking component registry...")
        async with session.get(f"{BACKEND_URL}/workflow/components") as resp:
            if resp.status != 200:
                print(f"❌ Failed to get components: {resp.status}")
                return
            
            result = await resp.json()
            if not result.get("success"):
                print(f"❌ Components API error: {result.get('error')}")
                return
            
            components = result.get("data", [])
            email_comp = None
            for comp in components:
                if comp['type'] == 'email_report':  # Look for type instead of name
                    email_comp = comp
                    break
            
            if not email_comp:
                print("❌ EmailReportComponent not found in registry")
                return
            
            print(f"✅ Found EmailReportComponent: {email_comp['name']}")
        
        # 2. Create workflow template
        print("\n2️⃣ Creating workflow template...")
        template_data = {
            "name": "Email Report Test Workflow",
            "description": "Test workflow for email reporting",
            "metadata": {
                "version": "1.0",
                "created_by": "test"
            },
            "workflow_data": {
                "nodes": [
                    {
                        "id": "email_sender",
                        "type": "email_report",
                        "data": {
                            "recipient_email": "vuducanhhn@gmail.com",
                            "subject_prefix": "Test Workflow Report",
                            "include_charts": True,
                            "report_type": "execution"
                        },
                        "position": {"x": 100, "y": 100}
                    }
                ],
                "edges": []
            }
        }
        
        async with session.post(
            f"{BACKEND_URL}/workflow/templates/",
            json=template_data
        ) as resp:
            if resp.status != 200:
                print(f"❌ Failed to create template: {resp.status}")
                print(await resp.text())
                return
            
            template = await resp.json()
            print(f"📋 Template response: {template}")
            template_id = template.get("id") or template.get("template_id") 
            if not template_id:
                print("❌ No template ID in response")
                return
            print(f"✅ Created template: {template_id}")
        
        # 3. Create workflow instance
        print("\n3️⃣ Creating workflow instance...")
        instance_data = {
            "template_id": template_id,
            "name": "Email Test Instance",
            "input_data": {}
        }
        
        async with session.post(
            f"{BACKEND_URL}/workflow/instances/",
            json=instance_data
        ) as resp:
            if resp.status != 200:
                print(f"❌ Failed to create instance: {resp.status}")
                print(await resp.text())
                return
            
            instance = await resp.json()
            print(f"📋 Instance response: {instance}")
            instance_id = instance.get("id") or instance.get("instance_id")
            if not instance_id:
                print("❌ No instance ID in response")
                return
            print(f"✅ Created instance: {instance_id}")
        
        # 4. Execute workflow
        print("\n4️⃣ Executing workflow...")
        async with session.post(
            f"{BACKEND_URL}/workflow/instances/{instance_id}/execute",
            json={}
        ) as resp:
            if resp.status != 200:
                print(f"❌ Failed to execute workflow: {resp.status}")
                print(await resp.text())
                return
            
            execution = await resp.json()
            print(f"📋 Execution response: {execution}")
            if not execution.get("success"):
                print("❌ Execution failed to start")
                return
            print(f"✅ Started execution for instance: {instance_id}")
        
        # 5. Monitor execution by checking instance status
        print("\n5️⃣ Monitoring execution...")
        for i in range(30):  # Wait up to 30 seconds
            await asyncio.sleep(1)
            
            async with session.get(
                f"{BACKEND_URL}/workflow/instances/{instance_id}"
            ) as resp:
                if resp.status != 200:
                    print(f"❌ Failed to get instance status: {resp.status}")
                    continue
                
                instance_status = await resp.json()
                status = instance_status.get("status", "unknown")
                print(f"⏳ Status: {status}")
                
                if status in ["completed", "failed", "error"]:
                    print(f"\n📊 Final Status: {status}")
                    
                    # Try to get execution details
                    executions = instance_status.get("executions", [])
                    if executions:
                        latest_execution = executions[-1]
                        steps = latest_execution.get("steps", [])
                        print(f"📋 Steps executed: {len(steps)}")
                        for step in steps:
                            step_status = step.get("status", "unknown")
                            step_name = step.get("component_type", "unknown")
                            error = step.get("error", "")
                            print(f"   - {step_name}: {step_status}")
                            if error:
                                print(f"     Error: {error}")
                    
                    if status == "completed":
                        print("✅ Workflow completed successfully!")
                        print("📧 Check your email for the report!")
                    else:
                        print("❌ Workflow failed")
                    
                    break
        else:
            print("⏰ Execution timed out")

if __name__ == "__main__":
    asyncio.run(test_email_component_in_workflow())
