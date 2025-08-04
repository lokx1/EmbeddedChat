"""
Demo Email Report System - Comprehensive Testing
Shows how the email report system works with real workflow data
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def create_realistic_workflow_execution():
    """Create realistic workflow execution data based on your current setup"""
    
    # Sample execution that matches your NEWUQW workflow
    execution_logs = [
        {
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'level': 'info',
            'message': 'Workflow NEWUQW started - Real Ollama Integration using qwen2.5:3b-m',
            'node_id': 'start-1',
            'execution_time': 50,
            'details': {
                'trigger_type': 'manual',
                'workflow_version': '1.0',
                'user': 'system'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=14)).isoformat(),
            'level': 'success',
            'message': 'Google Sheets connection established successfully',
            'node_id': 'sheets-read-2',
            'execution_time': 1200,
            'details': {
                'sheets_id': '1234567890abcdef',
                'worksheet': 'Sheet1',
                'range': 'A:E'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=13)).isoformat(),
            'level': 'success',
            'message': 'Successfully read 5 rows from Google Sheets',
            'node_id': 'sheets-read-2',
            'execution_time': 1200,
            'details': {
                'rows_read': 5,
                'headers': ['Description', 'Example Asset URL', 'Desired Output Format', 'Model Specification', 'Prompt'],
                'data_preview': [
                    'Winter Campaign assets needed',
                    'Summer Sale banner',
                    'Product showcase video',
                    'Brand awareness poster',
                    'Social media graphics'
                ]
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=12)).isoformat(),
            'level': 'info',
            'message': 'Starting AI processing with Ollama qwen2.5:3b model',
            'node_id': 'ai-processing-3',
            'execution_time': 8500,
            'details': {
                'provider': 'ollama',
                'model': 'qwen2.5:3b',
                'input_rows': 5,
                'processing_mode': 'batch'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'level': 'warning',
            'message': 'AI processing taking longer than expected for complex prompts',
            'node_id': 'ai-processing-3',
            'execution_time': 8500,
            'details': {
                'expected_time': '5000ms',
                'current_time': '6500ms',
                'reason': 'Complex asset generation requests'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=8)).isoformat(),
            'level': 'success',
            'message': 'AI processing completed successfully. Generated 4/5 responses',
            'node_id': 'ai-processing-3',
            'execution_time': 8500,
            'details': {
                'successful_generations': 4,
                'failed_generations': 1,
                'total_tokens_used': 12450,
                'average_response_length': 250,
                'model_performance': 'excellent'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=7)).isoformat(),
            'level': 'info',
            'message': 'Preparing to write results back to Google Sheets Prompt column',
            'node_id': 'sheets-write-4',
            'execution_time': 1800,
            'details': {
                'target_column': 'E (Prompt)',
                'rows_to_update': 4,
                'update_mode': 'append'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=6)).isoformat(),
            'level': 'error',
            'message': 'Failed to write to Google Sheets: Insufficient permissions for target range',
            'node_id': 'sheets-write-4',
            'execution_time': 1800,
            'details': {
                'error_code': 'PERMISSION_DENIED',
                'required_scope': 'https://www.googleapis.com/auth/spreadsheets',
                'current_scope': 'https://www.googleapis.com/auth/spreadsheets.readonly',
                'suggested_fix': 'Update OAuth scopes and re-authenticate'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'level': 'info',
            'message': 'Attempting automatic permission upgrade and retry',
            'node_id': 'sheets-write-4',
            'execution_time': 1200,
            'details': {
                'retry_attempt': 1,
                'strategy': 'permission_upgrade',
                'fallback_available': True
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=4)).isoformat(),
            'level': 'success',
            'message': 'Permission upgrade successful, retrying write operation',
            'node_id': 'sheets-write-4',
            'execution_time': 1200,
            'details': {
                'new_permissions': 'write_enabled',
                'retry_attempt': 1,
                'status': 'proceeding'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=3)).isoformat(),
            'level': 'success',
            'message': 'Successfully wrote 4 AI-generated responses to Prompt column',
            'node_id': 'sheets-write-4',
            'execution_time': 1200,
            'details': {
                'rows_updated': 4,
                'column': 'E',
                'update_range': 'E2:E5',
                'characters_written': 980,
                'format': 'plain_text'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=2)).isoformat(),
            'level': 'info',
            'message': 'Triggering notification workflow',
            'node_id': 'notification-5',
            'execution_time': 300,
            'details': {
                'notification_type': 'completion',
                'recipients': ['admin'],
                'channels': ['email']
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=1)).isoformat(),
            'level': 'success',
            'message': 'Workflow completed successfully with 1 retry and 4/5 successful AI generations',
            'node_id': 'end-6',
            'execution_time': 100,
            'details': {
                'total_duration': '14 minutes',
                'success_rate': '80%',
                'ai_tokens_used': 12450,
                'sheets_operations': 2,
                'retries_performed': 1,
                'final_status': 'completed_with_warnings'
            }
        }
    ]
    
    # Create corresponding events
    execution_events = [
        {
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'event_type': 'workflow_started',
            'data': {
                'instance_id': 'newuqw-exec-001',
                'workflow_name': 'NEWUQW - Real Ollama Integration using qwen2.5:3b-m',
                'trigger_type': 'manual'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=14)).isoformat(),
            'event_type': 'step_started',
            'data': {
                'node_id': 'sheets-read-2',
                'step_name': 'Google Sheets Read',
                'step_type': 'data_source'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=13)).isoformat(),
            'event_type': 'step_completed',
            'data': {
                'node_id': 'sheets-read-2',
                'step_name': 'Google Sheets Read',
                'execution_time_ms': 1200,
                'rows_processed': 5
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=12)).isoformat(),
            'event_type': 'step_started',
            'data': {
                'node_id': 'ai-processing-3',
                'step_name': 'AI Processing',
                'step_type': 'ai_generation'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=8)).isoformat(),
            'event_type': 'step_completed',
            'data': {
                'node_id': 'ai-processing-3',
                'step_name': 'AI Processing',
                'execution_time_ms': 8500,
                'results_generated': 4,
                'success_rate': 0.8
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=7)).isoformat(),
            'event_type': 'step_started',
            'data': {
                'node_id': 'sheets-write-4',
                'step_name': 'Google Sheets Write',
                'step_type': 'data_output'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=6)).isoformat(),
            'event_type': 'step_failed',
            'data': {
                'node_id': 'sheets-write-4',
                'step_name': 'Google Sheets Write',
                'error': 'Permission denied',
                'error_code': 'PERMISSION_DENIED'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'event_type': 'step_retried',
            'data': {
                'node_id': 'sheets-write-4',
                'step_name': 'Google Sheets Write (Retry)',
                'retry_attempt': 1,
                'strategy': 'permission_upgrade'
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=3)).isoformat(),
            'event_type': 'step_completed',
            'data': {
                'node_id': 'sheets-write-4',
                'step_name': 'Google Sheets Write (Retry)',
                'execution_time_ms': 1200,
                'rows_updated': 4,
                'retry_successful': True
            }
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=1)).isoformat(),
            'event_type': 'workflow_completed',
            'data': {
                'instance_id': 'newuqw-exec-001',
                'status': 'completed',
                'success_rate': 0.8,
                'total_duration_ms': 840000,
                'ai_generations': 4,
                'retries': 1
            }
        }
    ]
    
    return execution_logs, execution_events


def create_sample_analytics_data():
    """Create sample analytics data for daily report"""
    
    analytics_data = {
        'total_executions': 28,
        'successful_executions': 23,
        'failed_executions': 5,
        'average_execution_time': 420.5,  # seconds
        'success_rate_percentage': 82.1,
        'error_breakdown': {
            'Google Sheets Permission Error': 3,
            'AI Model Timeout': 1,
            'Network Connection Failed': 1
        },
        'performance_trend': [
            {'hour': 8, 'success_rate': 90.0, 'avg_time': 380.0, 'executions': 3},
            {'hour': 9, 'success_rate': 85.0, 'avg_time': 410.0, 'executions': 5},
            {'hour': 10, 'success_rate': 75.0, 'avg_time': 480.0, 'executions': 7},
            {'hour': 11, 'success_rate': 80.0, 'avg_time': 450.0, 'executions': 4},
            {'hour': 12, 'success_rate': 88.0, 'avg_time': 390.0, 'executions': 6},
            {'hour': 13, 'success_rate': 83.0, 'avg_time': 420.0, 'executions': 3}
        ],
        'top_workflows': [
            {'name': 'NEWUQW - Real Ollama Integration', 'executions': 12, 'success_rate': 91.7},
            {'name': 'Content Generation Pipeline', 'executions': 8, 'success_rate': 75.0},
            {'name': 'Data Analysis Workflow', 'executions': 5, 'success_rate': 80.0},
            {'name': 'Report Generation', 'executions': 3, 'success_rate': 100.0}
        ]
    }
    
    return analytics_data


def display_sample_email_structure():
    """Display what the email report would look like"""
    
    print("📧 EMAIL REPORT STRUCTURE PREVIEW")
    print("=" * 60)
    
    print("\n🔸 SUBJECT LINE:")
    print("✅ Workflow Report: NEWUQW - Real Ollama Integration (Completed)")
    
    print("\n🔸 EMAIL BODY (HTML):")
    print("""
    📊 Workflow Execution Report
    NEWUQW - Real Ollama Integration using qwen2.5:3b-m
    
    ═══════════════════════════════════════════════════════
    
    📊 EXECUTION SUMMARY
    Status: ✅ COMPLETED
    
    ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
    │   Duration      │  Success Rate   │ Steps Completed │     Errors      │
    │    14m 0s       │     80.0%       │      5/6        │       1         │
    └─────────────────┴─────────────────┴─────────────────┴─────────────────┘
    
    ℹ️ EXECUTION DETAILS
    Instance ID: newuqw-exec-001
    Start Time: 2025-08-04 14:45:00
    End Time: 2025-08-04 14:59:00
    Failed Steps: 1 (recovered via retry)
    
    📈 EXECUTION TIMELINE
    ✅ 14:45:00 - Workflow Started
    ✅ 14:46:00 - Google Sheets Read Completed (5 rows)
    ✅ 14:51:00 - AI Processing Completed (4/5 responses)
    ❌ 14:53:00 - Google Sheets Write Failed (Permission)
    🔄 14:54:00 - Google Sheets Write Retried
    ✅ 14:56:00 - Google Sheets Write Completed (4 rows)
    ✅ 14:59:00 - Workflow Completed
    
    🔴 ERROR SUMMARY
    14:53:00: Failed to write to Google Sheets: Insufficient permissions
    
    📋 DETAILED EXECUTION LOGS
    Showing 13 log entries. Full details in attached JSON file.
    
    [Log entries would be listed here...]
    
    ═══════════════════════════════════════════════════════
    Generated by EmbeddedChat Workflow System
    For detailed logs and raw data, please check attached files.
    """)
    
    print("\n🔸 ATTACHMENTS:")
    print("📊 workflow_analytics_newuqw-e.png - Performance charts and visualizations")
    print("📄 execution_details_newuqw-e.json - Complete logs and events data")
    
    print("\n🔸 ANALYTICS CHART CONTENTS:")
    print("📈 Success Rate Pie Chart (80% success, 20% failed)")
    print("📊 Execution Timeline (start → processing → completion)")
    print("📋 Step Summary (5 completed, 1 failed)")
    print("⏱️ Performance Metrics (duration, success rate, steps)")


def display_daily_report_structure():
    """Display what the daily analytics report would look like"""
    
    print("\n📊 DAILY ANALYTICS REPORT PREVIEW")
    print("=" * 60)
    
    print("\n🔸 SUBJECT LINE:")
    print("📊 Daily Workflow Analytics Report - 2025-08-04")
    
    print("\n🔸 EMAIL BODY (HTML):")
    print("""
    📊 Daily Workflow Analytics Report
    August 4, 2025
    
    ═══════════════════════════════════════════════════════
    
    📈 PERFORMANCE METRICS
    
    ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
    │ Total Executions│   Successful    │     Failed      │  Success Rate   │  Avg Duration   │
    │       28        │       23        │       5         │     82.1%       │    420.5s       │
    └─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
    
    🔍 ERROR BREAKDOWN
    • Google Sheets Permission Error: 3
    • AI Model Timeout: 1  
    • Network Connection Failed: 1
    
    📋 RECENT EXECUTIONS
    ┌────────────────────────────────────┬─────────┬──────────┬─────────────┐
    │             Workflow               │ Status  │ Duration │ Success Rate│
    ├────────────────────────────────────┼─────────┼──────────┼─────────────┤
    │ NEWUQW - Real Ollama Integration   │Completed│   14.0s  │    80.0%    │
    │ Content Generation Pipeline        │Completed│   25.3s  │    90.0%    │
    │ Data Analysis Workflow             │ Failed  │   45.1s  │     0.0%    │
    │ Report Generation                  │Completed│   12.8s  │   100.0%    │
    └────────────────────────────────────┴─────────┴──────────┴─────────────┘
    
    ═══════════════════════════════════════════════════════
    Generated by EmbeddedChat Workflow System
    Analytics chart attached. For detailed execution data, 
    please check the system logs.
    """)
    
    print("\n🔸 ATTACHMENTS:")
    print("📊 daily_analytics_20250804.png - Performance trends and metrics")


async def demo_api_usage():
    """Demo how to use the API endpoints"""
    
    print("\n🚀 API USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n🔸 SEND WORKFLOW EXECUTION REPORT:")
    print("POST /api/v1/workflow/instances/{instance_id}/send-report")
    print(json.dumps({
        "recipient_email": "admin@yourcompany.com",
        "include_analytics": True,
        "include_detailed_logs": True
    }, indent=2))
    
    print("\n🔸 SEND DAILY ANALYTICS REPORT:")
    print("POST /api/v1/workflow/reports/daily-analytics")
    print(json.dumps({
        "recipient_email": "manager@yourcompany.com",
        "date": "2025-08-04"
    }, indent=2))
    
    print("\n🔸 EXAMPLE CURL COMMANDS:")
    print("""
# Send execution report
curl -X POST http://localhost:8000/api/v1/workflow/instances/newuqw-exec-001/send-report \\
  -H "Content-Type: application/json" \\
  -d '{
    "recipient_email": "admin@yourcompany.com",
    "include_analytics": true,
    "include_detailed_logs": true
  }'

# Send daily analytics report  
curl -X POST http://localhost:8000/api/v1/workflow/reports/daily-analytics \\
  -H "Content-Type: application/json" \\
  -d '{
    "recipient_email": "manager@yourcompany.com",
    "date": "2025-08-04"
  }'
""")


def display_feature_summary():
    """Display comprehensive feature summary"""
    
    print("\n🎯 COMPREHENSIVE EMAIL REPORT FEATURES")
    print("=" * 60)
    
    features = {
        "📊 Workflow Execution Reports": [
            "✅ Success/failure status with detailed timeline",
            "📈 Analytics charts (success rate, performance metrics)",
            "🔍 Error breakdown and categorization", 
            "📋 Complete execution logs with node-level details",
            "📎 JSON attachments with raw data",
            "🎨 Professional HTML email formatting",
            "⏱️ Execution time and performance analysis"
        ],
        
        "📈 Daily Analytics Reports": [
            "📊 Comprehensive performance metrics dashboard",
            "📉 Success/failure rate trends over time",
            "🔍 Error breakdown by type and frequency",
            "📋 Recent executions summary table",
            "📈 Performance trend visualizations",
            "💾 Historical data comparison",
            "🎯 Key performance indicators (KPIs)"
        ],
        
        "🎨 Email Formatting Features": [
            "🖼️ Embedded analytics charts (PNG format)",
            "📱 Responsive HTML design",
            "🎨 Professional color scheme and typography",
            "📊 Interactive tables and data presentation",
            "📎 Multiple attachment support (JSON, images)",
            "🔍 Collapsible detail sections",
            "📧 Optimized for various email clients"
        ],
        
        "🔧 Technical Features": [
            "🚀 Asynchronous email sending (background tasks)",
            "📊 Matplotlib chart generation",
            "🔄 Automatic retry and error handling", 
            "💾 Persistent data storage integration",
            "🔌 SMTP configuration support",
            "📡 RESTful API endpoints",
            "🎯 Frontend UI integration"
        ]
    }
    
    for category, feature_list in features.items():
        print(f"\n{category}")
        for feature in feature_list:
            print(f"   {feature}")
    
    print("\n🎯 USE CASES:")
    print("   🔸 Workflow completion notifications")
    print("   🔸 Daily performance reports for managers")
    print("   🔸 Error analysis and troubleshooting")
    print("   🔸 Historical performance tracking")
    print("   🔸 Audit trails and compliance reporting")
    print("   🔸 Team productivity monitoring")


def main():
    """Main demo function"""
    
    print("🚀 EmbeddedChat Email Report Service - Comprehensive Demo")
    print("=" * 70)
    
    # 1. Show sample data structure
    print("\n1️⃣ SAMPLE WORKFLOW EXECUTION DATA:")
    logs, events = create_realistic_workflow_execution()
    print(f"   📋 Generated {len(logs)} detailed log entries")
    print(f"   📊 Generated {len(events)} execution events")
    print(f"   ⏱️ Total execution time: 14 minutes")
    print(f"   ✅ Success rate: 80% (4/5 AI generations successful)")
    print(f"   🔄 Retries performed: 1 (Google Sheets permission fix)")
    
    # 2. Show analytics data
    print("\n2️⃣ SAMPLE ANALYTICS DATA:")
    analytics = create_sample_analytics_data()
    print(f"   📊 Total executions today: {analytics['total_executions']}")
    print(f"   ✅ Success rate: {analytics['success_rate_percentage']:.1f}%")
    print(f"   ⏱️ Average execution time: {analytics['average_execution_time']:.1f}s")
    print(f"   🔍 Error types tracked: {len(analytics['error_breakdown'])}")
    print(f"   📈 Performance trend points: {len(analytics['performance_trend'])}")
    
    # 3. Show email structure
    display_sample_email_structure()
    display_daily_report_structure()
    
    # 4. Show API usage
    asyncio.run(demo_api_usage())
    
    # 5. Show comprehensive feature summary
    display_feature_summary()
    
    print("\n" + "=" * 70)
    print("💡 NEXT STEPS TO USE THIS SYSTEM:")
    print("=" * 70)
    print("1. 📧 Configure SMTP settings in your .env file:")
    print("   SMTP_SERVER=smtp.gmail.com")
    print("   SMTP_PORT=587") 
    print("   SMTP_USERNAME=your-email@gmail.com")
    print("   SMTP_PASSWORD=your-app-password")
    
    print("\n2. 🖥️ Start the backend server:")
    print("   cd backend && python -m uvicorn src.main:app --reload")
    
    print("\n3. 🌐 Start the frontend:")
    print("   cd frontend && npm start")
    
    print("\n4. 📧 Use the Email Report Panel in the UI:")
    print("   - Execute a workflow")
    print("   - Click the '📧' button in the Execution Panel")
    print("   - Enter recipient email and send report")
    
    print("\n5. 🔧 Or use the API directly:")
    print("   - POST /api/v1/workflow/instances/{id}/send-report")
    print("   - POST /api/v1/workflow/reports/daily-analytics")
    
    print("\n✨ Your comprehensive email reporting system is ready!")
    print("   📊 Professional HTML reports with charts")
    print("   📈 Daily analytics with performance metrics") 
    print("   🔍 Detailed error analysis and troubleshooting")
    print("   📎 JSON attachments for detailed data")
    print("   🎨 Beautiful, responsive email formatting")


if __name__ == "__main__":
    main()
