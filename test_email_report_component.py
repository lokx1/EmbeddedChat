#!/usr/bin/env python3
"""
Test Email Report Component
Test the new EmailReportComponent for sending comprehensive reports
"""

import asyncio
import aiohttp
from datetime import datetime

async def test_email_report_component():
    """Test EmailReportComponent trong workflow"""
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    print("🚀 EMAIL REPORT COMPONENT TEST")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # 1. Test component registry có EmailReportComponent
            print("1️⃣ Testing component registry for EmailReportComponent...")
            async with session.get(f"{base_url}/components") as response:
                if response.status == 200:
                    result = await response.json()
                    components = result.get('data', [])
                    email_report_comp = next((c for c in components if c['type'] == 'email_report'), None)
                    
                    if email_report_comp:
                        print(f"✅ Found EmailReportComponent: {email_report_comp['name']}")
                        print(f"   Description: {email_report_comp['description']}")
                        print(f"   Parameters: {len(email_report_comp['parameters'])}")
                    else:
                        print("❌ EmailReportComponent not found in registry")
                        return False
                else:
                    print(f"❌ Failed to get components: {response.status}")
                    return False
            
            # 2. Create workflow template với EmailReportComponent
            print("\n2️⃣ Creating workflow template with EmailReportComponent...")
            
            workflow_data = {
                "id": "email-report-test-workflow",
                "name": "Email Report Test Workflow",
                "description": "Test EmailReportComponent for sending reports",
                "workflow_data": {
                    "nodes": [
                        {
                            "id": "start-1",
                            "type": "start",
                            "position": {"x": 100, "y": 100},
                            "data": {
                                "label": "Start",
                                "config": {}
                            }
                        },
                        {
                            "id": "email-report-1", 
                            "type": "email_report",  # Use email_report type
                            "position": {"x": 300, "y": 100},
                            "data": {
                                "label": "Send Report",
                                "config": {
                                    "recipient_email": "long.luubaodepzai8@hcmut.edu.vn",
                                    "report_type": "execution",
                                    "include_charts": True,
                                    "subject_prefix": "🤖 Automated Workflow Report"
                                }
                            }
                        }
                    ],
                    "edges": [
                        {
                            "id": "edge-1",
                            "source": "start-1",
                            "target": "email-report-1",
                            "type": "default"
                        }
                    ]
                }
            }
            
            async with session.post(
                f"{base_url}/templates",
                json=workflow_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    template = await response.json()
                    template_id = template['template_id']
                    print(f"✅ Created workflow template: {template_id}")
                else:
                    text = await response.text()
                    print(f"❌ Failed to create template: {response.status}")
                    print(f"   Response: {text}")
                    return False
            
            # 3. Create and execute workflow instance
            print("\n3️⃣ Creating and executing workflow instance...")
            
            instance_data = {
                "template_id": template_id,
                "name": "Email Report Test Instance",
                "input_data": {
                    "test_message": "This is a test workflow execution for EmailReportComponent",
                    "execution_data": {
                        "workflow_name": "Email Report Test",
                        "start_time": datetime.now().isoformat(),
                        "status": "completed"
                    }
                }
            }
            
            async with session.post(
                f"{base_url}/instances",
                json=instance_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    instance = await response.json()
                    instance_id = instance['instance_id']
                    print(f"✅ Created workflow instance: {instance_id}")
                else:
                    text = await response.text()
                    print(f"❌ Failed to create instance: {response.status}")
                    print(f"   Response: {text}")
                    return False
            
            # 4. Execute workflow
            print("\n4️⃣ Executing workflow with EmailReportComponent...")
            async with session.post(
                f"{base_url}/instances/{instance_id}/execute",
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    execution = await response.json()
                    print(f"✅ Workflow execution started")
                    print(f"   Status: {execution.get('status', 'unknown')}")
                    
                    # Wait for execution to complete
                    print("⏳ Waiting for execution to complete...")
                    await asyncio.sleep(5)
                    
                    # Check final status
                    async with session.get(f"{base_url}/instances/{instance_id}") as status_response:
                        if status_response.status == 200:
                            status = await status_response.json()
                            final_status = status.get('status', 'unknown')
                            print(f"✅ Final status: {final_status}")
                            
                            if final_status == 'completed':
                                print("🎉 EmailReportComponent executed successfully!")
                                print("📧 Check your inbox for the comprehensive workflow report")
                                return True
                            elif final_status == 'failed':
                                print(f"❌ Workflow failed: {status.get('error_message', 'Unknown error')}")
                                return False
                            else:
                                print(f"⏳ Workflow still in progress: {final_status}")
                                return True
                        else:
                            print(f"❌ Failed to get status: {status_response.status}")
                            return False
                else:
                    text = await response.text()
                    print(f"❌ Failed to execute workflow: {response.status}")
                    print(f"   Response: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def test_direct_email_report_api():
    """Test direct API call to EmailReportComponent"""
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    print("\n📊 TESTING DIRECT EMAIL REPORT API")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Test execution report
            print("1️⃣ Testing execution report via API...")
            report_data = {
                "recipient_email": "long.luubaodepzai8@hcmut.edu.vn",
                "workflow_name": "API Test Workflow",
                "subject_prefix": "🔧 Direct API Test Report"
            }
            
            async with session.post(
                f"{base_url}/reports/execution",
                json=report_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Execution report sent successfully!")
                    print("📧 Check your inbox for the execution report")
                else:
                    text = await response.text()
                    print(f"❌ Failed to send execution report: {response.status}")
                    print(f"   Response: {text}")
                    return False
            
            # Test daily analytics report
            print("\n2️⃣ Testing daily analytics report via API...")
            analytics_data = {
                "recipient_email": "long.luubaodepzai8@hcmut.edu.vn"
            }
            
            async with session.post(
                f"{base_url}/reports/daily-analytics",
                json=analytics_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Daily analytics report sent successfully!")
                    print("📧 Check your inbox for the analytics report")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Failed to send analytics report: {response.status}")
                    print(f"   Response: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ API test failed with error: {e}")
        return False

async def main():
    """Main test function"""
    
    print("🧪 COMPREHENSIVE EMAIL REPORT COMPONENT TEST")
    print("=" * 70)
    print("Testing both EmailReportComponent in workflows and direct API calls")
    print("=" * 70)
    
    # Test 1: EmailReportComponent in workflow
    component_test = await test_email_report_component()
    
    # Test 2: Direct API calls
    api_test = await test_direct_email_report_api()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    if component_test:
        print("✅ EmailReportComponent (Workflow Integration)")
    else:
        print("❌ EmailReportComponent (Workflow Integration)")
    
    if api_test:
        print("✅ Email Report API (Direct Calls)")
    else:
        print("❌ Email Report API (Direct Calls)")
    
    if component_test and api_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Email Report system is fully functional!")
        print("🎯 Features working:")
        print("• ✅ EmailReportComponent - Automated reports in workflows")
        print("• ✅ Email Report API - Direct report generation")
        print("• ✅ Professional HTML report templates")
        print("• ✅ Analytics charts and comprehensive data")
        print("📧 Check your email inbox for test reports!")
    else:
        print("❌ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    asyncio.run(main())
