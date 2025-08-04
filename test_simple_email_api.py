#!/usr/bin/env python3
"""
Test EmailReportComponent execution qua API để bypass import issues
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "http://localhost:8000/api/v1"

async def test_email_component_api():
    print("🧪 TESTING EMAIL COMPONENT VIA API")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test execution report via API directly
        print("1️⃣ Testing execution report via API...")
        
        # Create a simple execution summary for testing
        execution_data = {
            "workflow_name": "Test Workflow",
            "instance_id": "test-instance-123",
            "status": "completed",
            "start_time": "2025-08-04T15:49:00Z",
            "end_time": "2025-08-04T15:50:00Z",
            "total_duration_seconds": 60,
            "total_steps": 3,
            "completed_steps": 3,
            "failed_steps": 0,
            "success_rate": 100.0,
            "errors": [],
            "warnings": []
        }
        
        report_data = {
            "recipient_email": "vuducanhhn@gmail.com",
            "workflow_execution": execution_data,
            "subject_prefix": "Test"
        }
        
        async with session.post(
            f"{BACKEND_URL}/workflow/reports/execution",
            json=report_data
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print("✅ Execution report sent successfully!")
                print(f"📧 Response: {result}")
            else:
                print(f"❌ Failed to send report: {resp.status}")
                print(await resp.text())
        
        # Test daily analytics report
        print("\n2️⃣ Testing daily analytics report via API...")
        
        analytics_data = {
            "recipient_email": "vuducanhhn@gmail.com",
            "date": "2025-08-04",
            "subject_prefix": "Test"
        }
        
        async with session.post(
            f"{BACKEND_URL}/workflow/reports/daily",
            json=analytics_data
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print("✅ Daily analytics report sent successfully!")
                print(f"📧 Response: {result}")
            else:
                print(f"❌ Failed to send analytics: {resp.status}")
                print(await resp.text())

if __name__ == "__main__":
    asyncio.run(test_email_component_api())
