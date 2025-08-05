#!/usr/bin/env python3
"""
Test EmailReportComponent trong workflow execution với debug chi tiết
"""

import asyncio
import aiohttp
import json
import time

BACKEND_URL = "http://localhost:8000/api/v1"

async def test_minimal_email_workflow():
    print("🧪 MINIMAL EMAIL WORKFLOW TEST")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Create minimal workflow với chỉ EmailReportComponent
        print("1️⃣ Creating minimal email workflow...")
        
        template_data = {
            "name": "Minimal Email Test",
            "description": "Just email component",
            "metadata": {},
            "nodes": [
                {
                    "id": "email_node",
                    "type": "email_report",  # Use correct type name
                    "data": {
                        "recipient_email": "vuducanhhn@gmail.com",
                        "report_title": "Minimal Test Report",
                        "include_charts": False,  # Disable charts for simplicity
                        "report_type": "execution"
                    },
                    "position": {"x": 100, "y": 100}
                }
            ],
            "edges": []
        }
        
        async with session.post(
            f"{BACKEND_URL}/workflow/templates/",
            json=template_data
        ) as resp:
            result = await resp.json()
            if not result.get("success"):
                print(f"❌ Template creation failed: {result}")
                return
            
            template_id = result["template_id"]
            print(f"✅ Created template: {template_id}")
        
        # Create instance
        print("\n2️⃣ Creating instance...")
        instance_data = {
            "template_id": template_id,
            "name": "Minimal Email Instance",
            "input_data": {}
        }
        
        async with session.post(
            f"{BACKEND_URL}/workflow/instances/",
            json=instance_data
        ) as resp:
            result = await resp.json()
            if not result.get("success"):
                print(f"❌ Instance creation failed: {result}")
                return
            
            instance_id = result["instance_id"]
            print(f"✅ Created instance: {instance_id}")
        
        # Execute workflow
        print("\n3️⃣ Executing workflow...")
        async with session.post(
            f"{BACKEND_URL}/workflow/instances/{instance_id}/execute",
            json={}
        ) as resp:
            result = await resp.json()
            if not result.get("success"):
                print(f"❌ Execution failed: {result}")
                return
            
            print(f"✅ Execution started: {result}")
        
        # Monitor với detailed logging
        print("\n4️⃣ Monitoring execution with detailed logs...")
        for i in range(20):  # Check for 20 seconds
            await asyncio.sleep(1)
            
            # Get instance status
            async with session.get(
                f"{BACKEND_URL}/workflow/instances/{instance_id}"
            ) as resp:
                if resp.status == 200:
                    instance_info = await resp.json()
                    status = instance_info.get("status", "unknown")
                    print(f"⏳ Instance status: {status}")
                    
                    if status in ["completed", "failed", "error"]:
                        print(f"\n📊 Final status: {status}")
                        
                        # Get execution logs
                        async with session.get(
                            f"{BACKEND_URL}/workflow/instances/{instance_id}/logs"
                        ) as logs_resp:
                            if logs_resp.status == 200:
                                logs = await logs_resp.json()
                                print(f"📋 Execution logs ({len(logs)} steps):")
                                for log in logs:
                                    step_status = log.get("status", "unknown")
                                    step_name = log.get("step_name", "unknown")
                                    error = log.get("error_message", "")
                                    print(f"   - {step_name}: {step_status}")
                                    if error:
                                        print(f"     Error: {error}")
                        
                        if status == "completed":
                            print("✅ Workflow completed! Check your email!")
                        
                        return
                else:
                    print(f"❌ Failed to get instance status: {resp.status}")
        
        print("⏰ Monitoring timed out")

if __name__ == "__main__":
    asyncio.run(test_minimal_email_workflow())
