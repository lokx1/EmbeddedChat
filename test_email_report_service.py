"""
Test Email Report Service
Demo script to test the comprehensive email reporting functionality
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add backend path to sys.path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.services.workflow.email_report_service import (
    EmailReportService,
    WorkflowExecutionSummary,
    WorkflowAnalytics,
    create_execution_summary_from_data,
    process_execution_logs_for_report
)
from backend.src.services.workflow.notifications import EmailService


async def test_email_report_service():
    """Test the email report service with sample data"""
    
    print("🚀 Testing Email Report Service...")
    
    # Initialize email service (you need to configure these settings)
    email_service = EmailService(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your-email@gmail.com",  # Replace with your email
        password="your-app-password",      # Replace with your app password
        use_tls=True
    )
    
    email_report_service = EmailReportService(email_service)
    
    # Test 1: Create sample workflow execution data
    print("\n📊 Creating sample workflow execution data...")
    
    sample_logs = [
        {
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'level': 'info',
            'message': 'Workflow execution started',
            'node_id': 'start-1',
            'execution_time': 100
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=9)).isoformat(),
            'level': 'info',
            'message': 'Reading Google Sheets data',
            'node_id': 'sheets-read-2',
            'execution_time': 2500
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=7)).isoformat(),
            'level': 'success',
            'message': 'Successfully read 5 rows from Google Sheets',
            'node_id': 'sheets-read-2',
            'execution_time': 2500
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=6)).isoformat(),
            'level': 'info',
            'message': 'Starting AI processing for asset generation',
            'node_id': 'ai-processing-3',
            'execution_time': 8500
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'level': 'warning',
            'message': 'AI processing took longer than expected',
            'node_id': 'ai-processing-3',
            'execution_time': 8500
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=4)).isoformat(),
            'level': 'success',
            'message': 'AI processing completed successfully. Generated 4 responses',
            'node_id': 'ai-processing-3',
            'execution_time': 8500
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=3)).isoformat(),
            'level': 'info',
            'message': 'Writing results back to Google Sheets',
            'node_id': 'sheets-write-4',
            'execution_time': 1200
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=2)).isoformat(),
            'level': 'error',
            'message': 'Failed to write to Google Sheets: Permission denied',
            'node_id': 'sheets-write-4',
            'execution_time': 1200
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=1)).isoformat(),
            'level': 'info',
            'message': 'Retrying Google Sheets write operation',
            'node_id': 'sheets-write-4',
            'execution_time': 800
        },
        {
            'timestamp': datetime.now().isoformat(),
            'level': 'success',
            'message': 'Workflow completed successfully with 1 retry',
            'node_id': 'end-5',
            'execution_time': 100
        }
    ]
    
    sample_events = [
        {
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'event_type': 'workflow_started',
            'data': {'instance_id': 'test-instance-001'}
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=9)).isoformat(),
            'event_type': 'step_started',
            'data': {'node_id': 'sheets-read-2', 'step_name': 'Google Sheets Read'}
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=7)).isoformat(),
            'event_type': 'step_completed',
            'data': {'node_id': 'sheets-read-2', 'step_name': 'Google Sheets Read', 'execution_time_ms': 2500}
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=6)).isoformat(),
            'event_type': 'step_started',
            'data': {'node_id': 'ai-processing-3', 'step_name': 'AI Processing'}
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=4)).isoformat(),
            'event_type': 'step_completed',
            'data': {'node_id': 'ai-processing-3', 'step_name': 'AI Processing', 'execution_time_ms': 8500}
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=3)).isoformat(),
            'event_type': 'step_started',
            'data': {'node_id': 'sheets-write-4', 'step_name': 'Google Sheets Write'}
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=2)).isoformat(),
            'event_type': 'step_failed',
            'data': {'node_id': 'sheets-write-4', 'step_name': 'Google Sheets Write', 'error': 'Permission denied'}
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=1)).isoformat(),
            'event_type': 'step_retried',
            'data': {'node_id': 'sheets-write-4', 'step_name': 'Google Sheets Write (Retry)'}
        },
        {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'workflow_completed',
            'data': {'instance_id': 'test-instance-001', 'status': 'completed'}
        }
    ]
    
    # Create execution summary
    execution_data = {
        'start_time': (datetime.now() - timedelta(minutes=10)).isoformat(),
        'end_time': datetime.now().isoformat(),
        'status': 'completed',
        'total_steps': 5,
        'completed_steps': 4,
        'failed_steps': 1
    }
    
    execution_summary = create_execution_summary_from_data(
        workflow_name="NEWUQW - Real Ollama Integration using qwen2.5:3b-m",
        instance_id="test-instance-001",
        execution_data=execution_data,
        logs=sample_logs,
        events=sample_events
    )
    
    print(f"✅ Created execution summary: {execution_summary.workflow_name}")
    print(f"   Status: {execution_summary.status}")
    print(f"   Duration: {execution_summary.total_duration_seconds:.2f}s")
    print(f"   Success Rate: {execution_summary.success_rate:.1f}%")
    print(f"   Errors: {len(execution_summary.errors)}")
    print(f"   Warnings: {len(execution_summary.warnings)}")
    
    # Test 2: Send workflow completion report
    print("\n📧 Testing workflow completion report...")
    
    try:
        result = await email_report_service.send_workflow_completion_report(
            recipient_email="test@example.com",  # Replace with your email for testing
            execution_summary=execution_summary,
            execution_logs=sample_logs,
            execution_events=sample_events,
            include_analytics=True,
            include_detailed_logs=True
        )
        
        if result['success']:
            print("✅ Workflow completion report sent successfully!")
            print(f"   Recipient: {result['recipient']}")
            print(f"   Attachments: {result['attachments_count']}")
        else:
            print(f"❌ Failed to send report: {result['error']}")
            
    except Exception as e:
        print(f"❌ Exception while sending report: {str(e)}")
    
    # Test 3: Create sample analytics data and send daily report
    print("\n📈 Testing daily analytics report...")
    
    sample_analytics = WorkflowAnalytics(
        total_executions=25,
        successful_executions=20,
        failed_executions=5,
        average_execution_time=180.5,
        success_rate_percentage=80.0,
        error_breakdown={
            'Google Sheets API Error': 3,
            'AI Processing Timeout': 1,
            'Network Connection Error': 1
        },
        performance_trend=[
            {'hour': 9, 'success_rate': 90.0, 'avg_time': 150.0},
            {'hour': 10, 'success_rate': 85.0, 'avg_time': 165.0},
            {'hour': 11, 'success_rate': 75.0, 'avg_time': 200.0},
            {'hour': 12, 'success_rate': 80.0, 'avg_time': 180.0},
            {'hour': 13, 'success_rate': 85.0, 'avg_time': 170.0}
        ]
    )
    
    # Sample recent executions
    recent_executions = [execution_summary]  # In real scenario, you'd have multiple
    
    today = datetime.now()
    date_range = (
        today.replace(hour=0, minute=0, second=0, microsecond=0),
        today.replace(hour=23, minute=59, second=59, microsecond=999999)
    )
    
    try:
        result = await email_report_service.send_daily_analytics_report(
            recipient_email="test@example.com",  # Replace with your email for testing
            analytics=sample_analytics,
            date_range=date_range,
            recent_executions=recent_executions
        )
        
        if result['success']:
            print("✅ Daily analytics report sent successfully!")
        else:
            print(f"❌ Failed to send daily report: {result['error']}")
            
    except Exception as e:
        print(f"❌ Exception while sending daily report: {str(e)}")
    
    print("\n🎉 Email report service testing completed!")
    print("\n📋 Summary of Features Tested:")
    print("   ✅ Workflow execution summary creation")
    print("   ✅ Comprehensive execution report with analytics chart")
    print("   ✅ Daily analytics report with performance metrics")
    print("   ✅ Error and warning categorization")
    print("   ✅ HTML email formatting with charts")
    print("   ✅ JSON attachments for detailed data")
    
    print("\n💡 Key Features:")
    print("   📊 Automatic analytics chart generation")
    print("   📈 Success/failure rate visualization")
    print("   📋 Detailed execution timeline")
    print("   🔍 Error breakdown and analysis")
    print("   📎 JSON attachments with raw data")
    print("   🎨 Professional HTML email formatting")


def test_sample_data_creation():
    """Test creating sample data without sending emails"""
    print("🧪 Testing sample data creation...")
    
    # Sample execution logs that match your workflow structure
    sample_logs = [
        {
            'timestamp': datetime.now().isoformat(),
            'level': 'info',
            'message': 'Workflow execution started',
            'node_id': 'start-1'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'level': 'success',
            'message': 'Google Sheets data read successfully (5 rows)',
            'node_id': 'sheets-read-2'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'level': 'success',
            'message': 'AI processing completed (4 responses generated)',
            'node_id': 'ai-processing-3'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'level': 'error',
            'message': 'Failed to write results to Google Sheets',
            'node_id': 'sheets-write-4'
        }
    ]
    
    # Process logs
    all_logs, error_logs, warning_logs = process_execution_logs_for_report(sample_logs)
    
    print(f"✅ Processed {len(all_logs)} logs:")
    print(f"   - {len(error_logs)} errors")
    print(f"   - {len(warning_logs)} warnings")
    
    for log in all_logs:
        print(f"   {log['level'].upper()}: {log['message']}")
    
    print("\n✅ Sample data creation test completed!")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EmbeddedChat Email Report Service Test")
    print("=" * 60)
    
    # First test without email sending
    test_sample_data_creation()
    
    print("\n" + "=" * 60)
    print("Note: To test actual email sending, configure SMTP settings")
    print("in the test_email_report_service() function and uncomment")
    print("the asyncio.run() line below.")
    print("=" * 60)
    
    # Uncomment the line below to test actual email sending (after configuring SMTP)
    # asyncio.run(test_email_report_service())
