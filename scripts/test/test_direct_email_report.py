#!/usr/bin/env python3
"""
Test direct email report API endpoints với email đúng
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "http://localhost:8000/api/v1/workflow"

async def test_direct_email_reports():
    print("🚀 TESTING DIRECT EMAIL REPORT ENDPOINTS")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test execution report
        print("1️⃣ Testing execution report...")
        execution_data = {
            "recipient_email": "longbaoluu68@gmail.com",
            "workflow_name": "Test Workflow",
            "instance_id": "test-instance-123"
        }
        
        async with session.post(
            f"{BACKEND_URL}/reports/execution",
            json=execution_data
        ) as resp:
            print(f"Status: {resp.status}")
            result = await resp.text()
            print(f"Response: {result}")
            
            if resp.status == 200:
                print("✅ Execution report sent successfully!")
                print("📧 Check email: longbaoluu68@gmail.com")
            else:
                print("❌ Failed to send execution report")
        
        print("\n" + "="*60)
        
        # Test daily analytics report
        print("2️⃣ Testing daily analytics report...")
        analytics_data = {
            "recipient_email": "longbaoluu68@gmail.com"
        }
        
        async with session.post(
            f"{BACKEND_URL}/reports/daily-analytics",
            json=analytics_data
        ) as resp:
            print(f"Status: {resp.status}")
            result = await resp.text()
            print(f"Response: {result}")
            
            if resp.status == 200:
                print("✅ Daily analytics report sent successfully!")
                print("📧 Check email: longbaoluu68@gmail.com")
            else:
                print("❌ Failed to send analytics report")

if __name__ == "__main__":
    asyncio.run(test_direct_email_reports())
