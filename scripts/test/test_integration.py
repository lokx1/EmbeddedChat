"""
Test Email System After Frontend/Backend Fix
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment from backend
load_dotenv("backend/.env")

# Add backend src to path  
backend_src = Path("backend/src")
sys.path.insert(0, str(backend_src))

async def test_email_system_integration():
    """Test complete email system integration"""
    print("🧪 TESTING EMAIL SYSTEM INTEGRATION")
    print("=" * 60)
    
    # Test 1: Configuration loading
    print("1️⃣ Testing configuration loading...")
    try:
        from core.config import settings
        print(f"✅ SMTP Server: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        print(f"✅ Username: {settings.SMTP_USERNAME}")
        print(f"✅ Use TLS: {settings.SMTP_USE_TLS}")
        
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            print("❌ Email credentials not configured")
            return False
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test 2: Email service creation
    print("\n2️⃣ Testing email service creation...")
    try:
        from services.workflow.notifications import EmailService
        
        email_service = EmailService(
            smtp_server=settings.SMTP_SERVER,
            smtp_port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_USE_TLS
        )
        print("✅ EmailService created successfully")
        
    except Exception as e:
        print(f"❌ EmailService error: {e}")
        return False
    
    # Test 3: Email report service
    print("\n3️⃣ Testing email report service...")
    try:
        from services.workflow.email_report_service import EmailReportService, WorkflowExecutionSummary
        from datetime import datetime
        
        report_service = EmailReportService(email_service)
        print("✅ EmailReportService created successfully")
        
        # Create mock data
        mock_summary = WorkflowExecutionSummary(
            workflow_name="Frontend Integration Test",
            instance_id="test-integration-001",
            status="completed",
            start_time=datetime.now().replace(minute=0, second=0, microsecond=0),
            end_time=datetime.now(),
            total_duration_seconds=180.5,
            total_steps=3,
            completed_steps=3,
            failed_steps=0,
            success_rate=100.0,
            errors=[],
            warnings=[]
        )
        
        mock_logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Frontend integration test workflow started",
                "step_id": "start"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Email component configured successfully",
                "step_id": "email_config"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "SUCCESS",
                "message": "Workflow completed successfully",
                "step_id": "complete"
            }
        ]
        
        mock_events = [
            {
                "event_type": "workflow.started",
                "timestamp": datetime.now().isoformat(),
                "data": {"workflow_id": "test-integration-001"}
            },
            {
                "event_type": "step.completed",
                "timestamp": datetime.now().isoformat(),
                "data": {"step_id": "email_config", "duration": 60.0}
            },
            {
                "event_type": "workflow.completed",
                "timestamp": datetime.now().isoformat(),
                "data": {"status": "success", "total_duration": 180.5}
            }
        ]
        
        print("✅ Mock data created")
        
    except Exception as e:
        print(f"❌ Email report service error: {e}")
        return False
    
    # Test 4: Send test email
    print("\n4️⃣ Testing email sending...")
    try:
        result = await report_service.send_workflow_completion_report(
            recipient_email=settings.SMTP_USERNAME,  # Send to self
            execution_summary=mock_summary,
            execution_logs=mock_logs,
            execution_events=mock_events,
            include_analytics=True,
            include_detailed_logs=True
        )
        
        if result.get("success"):
            print("✅ Test email sent successfully!")
            print("📧 Check your inbox for the integration test report")
        else:
            print(f"❌ Email sending failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False
    
    return True

async def test_api_compatibility():
    """Test API endpoint compatibility"""
    print("\n🔗 TESTING API COMPATIBILITY")
    print("=" * 60)
    
    # Test endpoint structure
    print("5️⃣ Testing API endpoint structure...")
    try:
        # Import workflow routes
        from api.routes.workflow import router
        print("✅ Workflow routes imported successfully")
        
        # Check if EmailService is properly imported
        from api.routes.workflow import EmailService
        print("✅ EmailService imported in routes")
        
        # Check if settings is used
        from core.config import settings
        print("✅ Settings accessible from routes")
        
    except Exception as e:
        print(f"❌ API compatibility error: {e}")
        return False
    
    return True

def test_frontend_components():
    """Check frontend component files exist"""
    print("\n🎨 CHECKING FRONTEND COMPONENTS")
    print("=" * 60)
    
    frontend_files = [
        "frontend/src/components/WorkflowEditor/EmailReportPanel.tsx",
        "frontend/src/components/WorkflowEditor/EnhancedExecutionPanel.tsx",
        "frontend/src/components/WorkflowEditor/NodeConfigPanel.tsx"
    ]
    
    print("6️⃣ Checking frontend files...")
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            return False
    
    # Check for email case in NodeConfigPanel
    print("\n7️⃣ Checking email case in NodeConfigPanel...")
    try:
        with open("frontend/src/components/WorkflowEditor/NodeConfigPanel.tsx", 'r') as f:
            content = f.read()
            if "case 'email':" in content:
                print("✅ Email case found in NodeConfigPanel")
            else:
                print("❌ Email case not found in NodeConfigPanel")
                return False
    except Exception as e:
        print(f"❌ Error checking NodeConfigPanel: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🚀 EMAIL SYSTEM INTEGRATION TEST")
    print("=" * 70)
    print("Testing complete email system after Frontend/Backend fixes")
    print("=" * 70)
    
    # Run all tests
    backend_ok = await test_email_system_integration()
    api_ok = await test_api_compatibility()
    frontend_ok = test_frontend_components()
    
    print("\n" + "=" * 70)
    print("📋 INTEGRATION TEST RESULTS")
    print("=" * 70)
    print(f"{'✅' if backend_ok else '❌'} Backend Email System")
    print(f"{'✅' if api_ok else '❌'} API Compatibility") 
    print(f"{'✅' if frontend_ok else '❌'} Frontend Components")
    
    if backend_ok and api_ok and frontend_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Email system is ready for production!")
        print()
        print("🚀 Next steps:")
        print("1. Start backend: cd backend && python -m uvicorn src.main:app --reload")
        print("2. Start frontend: cd frontend && npm start")
        print("3. Test Email Sender component in workflow editor")
        print("4. Test Email Report Panel in execution results")
        print()
        print("📧 Features available:")
        print("• Email Sender component for workflows")
        print("• Email Report Panel for execution results")
        print("• API endpoints for programmatic access")
        print("• Professional HTML email templates")
        
    else:
        print("\n❌ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    asyncio.run(main())
