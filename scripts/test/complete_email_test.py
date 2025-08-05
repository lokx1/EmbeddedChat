"""
Complete Email System Test
Test EmailService và EmailReportService hoàn chỉnh
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv("backend/.env")

# Add backend src to path
backend_src = Path("backend/src")
sys.path.insert(0, str(backend_src))

async def test_complete_email_system():
    """Test complete email system"""
    print("🎯 COMPLETE EMAIL SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Import services
        from services.workflow.notifications import EmailService
        from services.workflow.email_report_service import EmailReportService, WorkflowExecutionSummary
        from datetime import datetime
        
        print("✅ All services imported successfully!")
        
        # Create EmailService
        email_service = EmailService(
            smtp_server=os.getenv("SMTP_SERVER"),
            smtp_port=int(os.getenv("SMTP_PORT")),
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        )
        
        print("✅ EmailService created successfully!")
        
        # Create EmailReportService
        report_service = EmailReportService(email_service)
        print("✅ EmailReportService created successfully!")
        
        # Test basic email
        print("\n📤 Testing basic email...")
        email_result = await email_service.send_email(
            to_email="long.luubaodepzai8@hcmut.edu.vn",
            subject="🧪 EmbeddedChat Email Test",
            body="""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: green;">✅ Email Service Test Successful!</h2>
                <p>Your EmailService is working correctly!</p>
                <ul>
                    <li>SMTP Server: smtp.gmail.com:587</li>
                    <li>Authentication: ✅ Success</li>
                    <li>Email Delivery: ✅ Success</li>
                </ul>
                <p><strong>EmbeddedChat Email System is ready! 🚀</strong></p>
            </body>
            </html>
            """,
            from_email=f"EmbeddedAI <{os.getenv('SMTP_FROM_EMAIL')}>",
            is_html=True
        )
        
        if email_result.get("success"):
            print("✅ Basic email sent successfully!")
        else:
            print(f"❌ Basic email failed: {email_result.get('error')}")
            return False
        
        # Test workflow report
        print("\n📊 Testing workflow completion report...")
        
        # Create mock execution summary
        execution_summary = WorkflowExecutionSummary(
            workflow_name="Test Email Workflow",
            instance_id="test-workflow-001",
            status="completed",
            start_time=datetime.now().replace(minute=0, second=0, microsecond=0),
            end_time=datetime.now(),
            total_duration_seconds=300.5,
            total_steps=5,
            completed_steps=5,
            failed_steps=0,
            success_rate=100.0,
            errors=[],
            warnings=[]
        )
        
        # Mock execution logs
        execution_logs = [
            {
                "timestamp": "2025-08-04T10:00:00Z",
                "level": "INFO",
                "message": "Workflow started",
                "step_id": "init"
            },
            {
                "timestamp": "2025-08-04T10:02:30Z",
                "level": "INFO", 
                "message": "Data processing completed",
                "step_id": "process"
            },
            {
                "timestamp": "2025-08-04T10:05:00Z",
                "level": "INFO",
                "message": "Workflow completed successfully",
                "step_id": "complete"
            }
        ]
        
        # Mock execution events
        execution_events = [
            {
                "event_type": "workflow.started",
                "timestamp": "2025-08-04T10:00:00Z",
                "data": {"workflow_id": "test-workflow-001"}
            },
            {
                "event_type": "step.completed",
                "timestamp": "2025-08-04T10:02:30Z", 
                "data": {"step_id": "process", "duration": 150.0}
            },
            {
                "event_type": "workflow.completed",
                "timestamp": "2025-08-04T10:05:00Z",
                "data": {"status": "success", "total_duration": 300.5}
            }
        ]
        
        # Send workflow report
        report_result = await report_service.send_workflow_completion_report(
            recipient_email="long.luubaodepzai8@hcmut.edu.vn",
            execution_summary=execution_summary,
            execution_logs=execution_logs,
            execution_events=execution_events,
            include_analytics=True,
            include_detailed_logs=True
        )
        
        if report_result.get("success"):
            print("✅ Workflow completion report sent successfully!")
        else:
            print(f"❌ Workflow report failed: {report_result.get('error')}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ System test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 EMBEDDEDCHAT EMAIL SYSTEM")
    print("=" * 60)
    
    # Show configuration
    print("📋 Email Configuration:")
    print(f"• SMTP Server: {os.getenv('SMTP_SERVER')}:{os.getenv('SMTP_PORT')}")
    print(f"• Username: {os.getenv('SMTP_USERNAME')}")
    print(f"• From Email: {os.getenv('SMTP_FROM_EMAIL')}")
    print(f"• From Name: {os.getenv('SMTP_FROM_NAME')}")
    print(f"• Use TLS: {os.getenv('SMTP_USE_TLS')}")
    print()
    
    # Run complete test
    success = await test_complete_email_system()
    
    print("\n" + "="*60)
    if success:
        print("🎉 EMAIL SYSTEM TEST SUCCESSFUL!")
        print("✅ All components working correctly:")
        print("   • EmailService - Basic email sending")
        print("   • EmailReportService - Workflow reports") 
        print("   • SMTP Configuration - Authentication & delivery")
        print("   • HTML Templates - Professional formatting")
        print()
        print("📧 Check your email inbox for test messages!")
        print()
        print("🚀 Your EmbeddedChat Email Report System is ready!")
        print()
        print("📖 Usage:")
        print("   • Start backend: cd backend && python -m uvicorn src.main:app --reload")
        print("   • Start frontend: cd frontend && npm start")
        print("   • Use Email Report Panel in Workflow Editor")
        print("   • Call API endpoints for automation")
        print()
        print("🎯 Features available:")
        print("   • Comprehensive workflow execution reports")
        print("   • Daily analytics with charts")
        print("   • Professional HTML email templates")
        print("   • API integration for automation")
        
    else:
        print("❌ EMAIL SYSTEM TEST FAILED")
        print("Please check the error messages above")
        print()
        print("🛠️  Common solutions:")
        print("   • Verify App Password is correct")
        print("   • Check 2-Step Verification is enabled")
        print("   • Ensure firewall allows SMTP connections")
        print("   • Try generating new App Password")

if __name__ == "__main__":
    asyncio.run(main())
