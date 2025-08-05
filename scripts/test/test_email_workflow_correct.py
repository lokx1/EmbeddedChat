#!/usr/bin/env python3
"""
Test EmailReportComponent trong workflow với email đúng
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "http://localhost:8000/api/v1"

async def test_email_report_in_workflow():
    print("🚀 TESTING EMAIL REPORT COMPONENT IN WORKFLOW")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Create workflow template with EmailReportComponent
        print("1️⃣ Creating workflow template...")
        template_data = {
            "name": "Email Report Test - Correct Email",
            "description": "Test workflow for email reporting với email đúng",
            "metadata": {
                "version": "1.0",
                "created_by": "test"
            },
            "workflow_data": {
                "nodes": [
                    {
                        "id": "manual_trigger",
                        "type": "manual_trigger",
                        "data": {},
                        "position": {"x": 100, "y": 100}
                    },
                    {
                        "id": "email_report",
                        "type": "email_report",
                        "data": {
                            "recipient_email": "longbaoluu68@gmail.com",
                            "subject_prefix": "Test Workflow Report",
                            "include_charts": True,
                            "report_type": "execution"
                        },
                        "position": {"x": 300, "y": 100}
                    }
                ],
                "edges": [
                    {
                        "id": "edge_1",
                        "source": "manual_trigger",
                        "target": "email_report",
                        "sourceHandle": "output",
                        "targetHandle": "input"
                    }
                ]
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
            template_id = template.get("template_id")
            print(f"✅ Created template: {template_id}")
        
        # 2. Create workflow instance
        print("\n2️⃣ Creating workflow instance...")
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
            instance_id = instance.get("instance_id")
            print(f"✅ Created instance: {instance_id}")
        
        # 3. Execute workflow
        print("\n3️⃣ Executing workflow...")
        async with session.post(
            f"{BACKEND_URL}/workflow/instances/{instance_id}/execute",
            json={}
        ) as resp:
            if resp.status != 200:
                print(f"❌ Failed to execute workflow: {resp.status}")
                print(await resp.text())
                return
            
            execution = await resp.json()
            print(f"✅ Started execution for instance: {instance_id}")
        
        # 4. Monitor execution
        print("\n4️⃣ Monitoring execution...")
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
                print(f"⏳ Status: {status} (attempt {i+1}/30)")
                
                if status in ["completed", "failed", "error"]:
                    print(f"\n📊 Final Status: {status}")
                    
                    # Get execution steps
                    async with session.get(
                        f"{BACKEND_URL}/workflow/instances/{instance_id}/logs"
                    ) as logs_resp:
                        if logs_resp.status == 200:
                            logs_data = await logs_resp.json()
                            steps = logs_data.get("logs", [])
                            print(f"📋 Steps executed: {len(steps)}")
                            for step in steps:
                                step_status = step.get("status", "unknown")
                                step_name = step.get("step_name", "unknown")
                                error = step.get("error_message", "")
                                print(f"   - {step_name}: {step_status}")
                                if error:
                                    print(f"     Error: {error}")
                    
                    if status == "completed":
                        print("✅ Workflow completed successfully!")
                        print("📧 Check email: longbaoluu68@gmail.com")
                    else:
                        print("❌ Workflow failed")
                    
                    break
        else:
            print("⏰ Execution timed out")

if __name__ == "__main__":
    asyncio.run(test_email_report_in_workflow())
