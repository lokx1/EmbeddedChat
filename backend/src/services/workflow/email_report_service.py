"""
Comprehensive Email Report Service
Sends detailed workflow execution reports with analytics and charts
"""
import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib

from .notifications import EmailService


@dataclass
class WorkflowExecutionSummary:
    """Summary of workflow execution for reporting"""
    workflow_name: str
    instance_id: str
    status: str  # 'completed', 'failed', 'running', 'stopped'
    start_time: datetime
    end_time: Optional[datetime]
    total_duration_seconds: float
    total_steps: int
    completed_steps: int
    failed_steps: int
    success_rate: float
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    
    
@dataclass
class WorkflowAnalytics:
    """Analytics data for workflow performance"""
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    success_rate_percentage: float
    error_breakdown: Dict[str, int]
    performance_trend: List[Dict[str, Any]]
    

class EmailReportService:
    """Service for generating and sending comprehensive workflow reports"""
    
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
        
    async def send_workflow_completion_report(
        self,
        recipient_email: str,
        execution_summary: WorkflowExecutionSummary,
        execution_logs: List[Dict[str, Any]],
        execution_events: List[Dict[str, Any]],
        include_analytics: bool = True,
        include_detailed_logs: bool = True
    ) -> Dict[str, Any]:
        """
        Send a comprehensive workflow completion report
        
        Args:
            recipient_email: Email address to send report to
            execution_summary: Summary of workflow execution
            execution_logs: Detailed execution logs
            execution_events: Execution events
            include_analytics: Whether to include analytics chart
            include_detailed_logs: Whether to include full log details
        """
        try:
            # Generate report content
            html_content = await self._generate_report_html(
                execution_summary, 
                execution_logs, 
                execution_events,
                include_detailed_logs
            )
            
            # Generate analytics chart if requested
            chart_attachment = None
            if include_analytics:
                chart_attachment = await self._generate_analytics_chart(execution_summary)
            
            # Prepare email
            subject = self._generate_subject(execution_summary)
            
            # Prepare attachments
            attachments = []
            if chart_attachment:
                attachments.append({
                    'filename': f'workflow_analytics_{execution_summary.instance_id[:8]}.png',
                    'content': chart_attachment,
                    'mime_type': 'image/png'
                })
            
            # Add detailed logs as JSON attachment
            if include_detailed_logs:
                logs_json = json.dumps({
                    'execution_summary': {
                        'workflow_name': execution_summary.workflow_name,
                        'instance_id': execution_summary.instance_id,
                        'status': execution_summary.status,
                        'start_time': execution_summary.start_time.isoformat(),
                        'end_time': execution_summary.end_time.isoformat() if execution_summary.end_time else None,
                        'duration_seconds': execution_summary.total_duration_seconds,
                        'success_rate': execution_summary.success_rate,
                        'total_steps': execution_summary.total_steps,
                        'completed_steps': execution_summary.completed_steps,
                        'failed_steps': execution_summary.failed_steps
                    },
                    'logs': execution_logs,
                    'events': execution_events
                }, indent=2, default=str)
                
                attachments.append({
                    'filename': f'execution_details_{execution_summary.instance_id[:8]}.json',
                    'content': logs_json.encode('utf-8'),
                    'mime_type': 'application/json'
                })
            
            # Send email
            result = await self.email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                body=html_content,
                attachments=attachments,
                is_html=True
            )
            
            return {
                'success': True,
                'message': 'Comprehensive report sent successfully',
                'recipient': recipient_email,
                'attachments_count': len(attachments),
                **result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send report: {str(e)}',
                'recipient': recipient_email
            }
    
    async def send_daily_analytics_report(
        self,
        recipient_email: str,
        analytics: WorkflowAnalytics,
        date_range: Tuple[datetime, datetime],
        recent_executions: List[WorkflowExecutionSummary]
    ) -> Dict[str, Any]:
        """
        Send daily analytics report with comprehensive metrics
        """
        try:
            # Generate analytics chart
            chart_data = await self._generate_daily_analytics_chart(analytics, date_range)
            
            # Generate HTML report
            html_content = await self._generate_daily_report_html(
                analytics, 
                date_range, 
                recent_executions
            )
            
            subject = f"Daily Workflow Analytics Report - {date_range[1].strftime('%Y-%m-%d')}"
            
            attachments = []
            if chart_data:
                attachments.append({
                    'filename': f'daily_analytics_{date_range[1].strftime("%Y%m%d")}.png',
                    'content': chart_data,
                    'mime_type': 'image/png'
                })
            
            result = await self.email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                body=html_content,
                attachments=attachments,
                is_html=True
            )
            
            return {
                'success': True,
                'message': 'Daily analytics report sent successfully',
                **result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send daily report: {str(e)}'
            }
    
    def _generate_subject(self, summary: WorkflowExecutionSummary) -> str:
        """Generate email subject based on execution status"""
        status_icon = {
            'completed': '✅',
            'failed': '❌',
            'running': '🔄',
            'stopped': '⏹️'
        }.get(summary.status, '📊')
        
        return f"{status_icon} Workflow Report: {summary.workflow_name} ({summary.status.title()})"
    
    async def _generate_report_html(
        self,
        summary: WorkflowExecutionSummary,
        logs: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        include_detailed_logs: bool = True
    ) -> str:
        """Generate comprehensive HTML report"""
        
        # Status styling
        status_color = {
            'completed': '#10B981',  # green
            'failed': '#EF4444',     # red
            'running': '#F59E0B',    # yellow
            'stopped': '#6B7280'     # gray
        }.get(summary.status, '#6B7280')
        
        status_icon = {
            'completed': '✅',
            'failed': '❌',
            'running': '🔄',
            'stopped': '⏹️'
        }.get(summary.status, '📊')
        
        # Calculate metrics
        duration_str = f"{summary.total_duration_seconds:.2f}s"
        if summary.total_duration_seconds > 60:
            minutes = int(summary.total_duration_seconds // 60)
            seconds = summary.total_duration_seconds % 60
            duration_str = f"{minutes}m {seconds:.1f}s"
        
        # Process events for timeline
        event_timeline = ""
        if events:
            event_timeline = "<h3>📈 Execution Timeline</h3><div class='timeline'>"
            for event in events[-10:]:  # Show last 10 events
                event_time = event.get('timestamp', '')
                event_type = event.get('event_type', 'Unknown')
                event_status = 'success' if 'completed' in event_type.lower() else 'info'
                if 'failed' in event_type.lower() or 'error' in event_type.lower():
                    event_status = 'error'
                
                event_timeline += f"""
                <div class='timeline-item {event_status}'>
                    <div class='timeline-time'>{event_time}</div>
                    <div class='timeline-content'>{event_type.replace('_', ' ').title()}</div>
                </div>
                """
            event_timeline += "</div>"
        
        # Process logs for summary
        error_logs = [log for log in logs if log.get('level') == 'error']
        warning_logs = [log for log in logs if log.get('level') == 'warning']
        
        error_section = ""
        if error_logs:
            error_section = "<h3>🔴 Error Summary</h3><div class='error-summary'>"
            for error in error_logs[:5]:  # Show top 5 errors
                error_section += f"""
                <div class='error-item'>
                    <strong>{error.get('timestamp', 'Unknown time')}</strong>: {error.get('message', 'No message')}
                </div>
                """
            error_section += "</div>"
        
        warning_section = ""
        if warning_logs:
            warning_section = "<h3>🟡 Warning Summary</h3><div class='warning-summary'>"
            for warning in warning_logs[:3]:  # Show top 3 warnings
                warning_section += f"""
                <div class='warning-item'>
                    <strong>{warning.get('timestamp', 'Unknown time')}</strong>: {warning.get('message', 'No message')}
                </div>
                """
            warning_section += "</div>"
        
        # Detailed logs section
        detailed_logs_section = ""
        if include_detailed_logs and logs:
            detailed_logs_section = f"""
            <h3>📋 Detailed Execution Logs</h3>
            <div class='logs-container'>
                <p><em>Showing {len(logs)} log entries. Full details available in attached JSON file.</em></p>
                <div class='logs-preview'>
            """
            for log in logs[-20:]:  # Show last 20 logs
                log_level = log.get('level', 'info')
                log_icon = {'error': '🔴', 'warning': '🟡', 'info': 'ℹ️', 'success': '✅'}.get(log_level, 'ℹ️')
                detailed_logs_section += f"""
                <div class='log-entry {log_level}'>
                    <span class='log-time'>{log.get('timestamp', '')}</span>
                    <span class='log-level'>{log_icon} {log_level.upper()}</span>
                    <span class='log-message'>{log.get('message', '')}</span>
                </div>
                """
            detailed_logs_section += "</div></div>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Workflow Execution Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f8fafc; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
                .content {{ padding: 30px; }}
                .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; color: white; background-color: {status_color}; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 25px 0; }}
                .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: 700; color: #1a202c; margin-bottom: 5px; }}
                .metric-label {{ font-size: 14px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }}
                .timeline {{ margin: 20px 0; }}
                .timeline-item {{ display: flex; align-items: center; padding: 10px; margin: 5px 0; border-radius: 6px; }}
                .timeline-item.success {{ background: #f0fdf4; border-left: 4px solid #10b981; }}
                .timeline-item.info {{ background: #eff6ff; border-left: 4px solid #3b82f6; }}
                .timeline-item.error {{ background: #fef2f2; border-left: 4px solid #ef4444; }}
                .timeline-time {{ font-size: 12px; color: #6b7280; margin-right: 15px; min-width: 80px; }}
                .timeline-content {{ font-weight: 500; }}
                .error-summary, .warning-summary {{ margin: 15px 0; }}
                .error-item, .warning-item {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 12px; margin: 8px 0; }}
                .warning-item {{ background: #fffbeb; border-color: #fed7aa; }}
                .logs-container {{ margin: 20px 0; }}
                .logs-preview {{ max-height: 400px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 6px; }}
                .log-entry {{ display: flex; align-items: center; padding: 8px 12px; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
                .log-entry:last-child {{ border-bottom: none; }}
                .log-entry.error {{ background: #fef2f2; }}
                .log-entry.warning {{ background: #fffbeb; }}
                .log-entry.success {{ background: #f0fdf4; }}
                .log-time {{ color: #6b7280; margin-right: 10px; min-width: 80px; font-size: 11px; }}
                .log-level {{ margin-right: 10px; min-width: 60px; font-weight: 600; }}
                .log-message {{ flex: 1; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
                h2, h3 {{ color: #1a202c; margin-top: 30px; margin-bottom: 15px; }}
                h2 {{ font-size: 20px; }}
                h3 {{ font-size: 16px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_icon} Workflow Execution Report</h1>
                    <p>{summary.workflow_name}</p>
                </div>
                
                <div class="content">
                    <h2>📊 Execution Summary</h2>
                    <div style="margin: 20px 0;">
                        <span class="status-badge">{summary.status.title()}</span>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{duration_str}</div>
                            <div class="metric-label">Total Duration</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{summary.success_rate:.1f}%</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{summary.completed_steps}/{summary.total_steps}</div>
                            <div class="metric-label">Steps Completed</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{len(error_logs)}</div>
                            <div class="metric-label">Errors</div>
                        </div>
                    </div>
                    
                    <h2>ℹ️ Execution Details</h2>
                    <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                        <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">Instance ID:</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{summary.instance_id}</td></tr>
                        <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">Start Time:</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{summary.start_time.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                        <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">End Time:</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{summary.end_time.strftime('%Y-%m-%d %H:%M:%S') if summary.end_time else 'N/A'}</td></tr>
                        <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">Failed Steps:</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{summary.failed_steps}</td></tr>
                    </table>
                    
                    {event_timeline}
                    {error_section}
                    {warning_section}
                    {detailed_logs_section}
                </div>
                
                <div class="footer">
                    <p>Generated by EmbeddedChat Workflow System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>For detailed logs and raw data, please check the attached files.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    async def _generate_daily_report_html(
        self,
        analytics: WorkflowAnalytics,
        date_range: Tuple[datetime, datetime],
        recent_executions: List[WorkflowExecutionSummary]
    ) -> str:
        """Generate daily analytics report HTML"""
        
        start_date = date_range[0].strftime('%Y-%m-%d')
        end_date = date_range[1].strftime('%Y-%m-%d')
        
        # Recent executions table
        executions_table = ""
        if recent_executions:
            executions_table = """
            <h3>📋 Recent Executions</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <thead>
                    <tr style="background: #f8fafc;">
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e2e8f0;">Workflow</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e2e8f0;">Status</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e2e8f0;">Duration</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e2e8f0;">Success Rate</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for execution in recent_executions[-10:]:  # Show last 10
                status_color = {'completed': '#10B981', 'failed': '#EF4444'}.get(execution.status, '#6B7280')
                duration_str = f"{execution.total_duration_seconds:.1f}s"
                
                executions_table += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #f1f5f9;">{execution.workflow_name}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #f1f5f9;"><span style="color: {status_color}; font-weight: 600;">{execution.status.title()}</span></td>
                    <td style="padding: 10px; border-bottom: 1px solid #f1f5f9;">{duration_str}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #f1f5f9;">{execution.success_rate:.1f}%</td>
                </tr>
                """
            
            executions_table += "</tbody></table>"
        
        # Error breakdown
        error_breakdown_html = ""
        if analytics.error_breakdown:
            error_breakdown_html = """
            <h3>🔍 Error Breakdown</h3>
            <div style="margin: 15px 0;">
            """
            for error_type, count in analytics.error_breakdown.items():
                error_breakdown_html += f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 12px; margin: 5px 0; background: #fef2f2; border-radius: 6px; border-left: 4px solid #ef4444;">
                    <span>{error_type}</span>
                    <span style="font-weight: 600; color: #ef4444;">{count}</span>
                </div>
                """
            error_breakdown_html += "</div>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Daily Workflow Analytics Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f8fafc; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
                .content {{ padding: 30px; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 25px 0; }}
                .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: 700; color: #1a202c; margin-bottom: 5px; }}
                .metric-label {{ font-size: 14px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
                h2, h3 {{ color: #1a202c; margin-top: 30px; margin-bottom: 15px; }}
                h2 {{ font-size: 20px; }}
                h3 {{ font-size: 16px; }}
                table {{ border-collapse: collapse; }}
                th, td {{ text-align: left; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Daily Workflow Analytics Report</h1>
                    <p>{start_date} to {end_date}</p>
                </div>
                
                <div class="content">
                    <h2>📈 Performance Metrics</h2>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{analytics.total_executions}</div>
                            <div class="metric-label">Total Executions</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{analytics.successful_executions}</div>
                            <div class="metric-label">Successful</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{analytics.failed_executions}</div>
                            <div class="metric-label">Failed</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{analytics.success_rate_percentage:.1f}%</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{analytics.average_execution_time:.1f}s</div>
                            <div class="metric-label">Avg Duration</div>
                        </div>
                    </div>
                    
                    {error_breakdown_html}
                    {executions_table}
                </div>
                
                <div class="footer">
                    <p>Generated by EmbeddedChat Workflow System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Analytics chart attached. For detailed execution data, please check the system logs.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    async def _generate_analytics_chart(self, summary: WorkflowExecutionSummary) -> bytes:
        """Generate analytics chart for single workflow execution"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f'Workflow Analytics: {summary.workflow_name}', fontsize=16, fontweight='bold')
            
            # Chart 1: Success Rate Pie Chart
            labels = ['Completed', 'Failed']
            sizes = [summary.completed_steps, summary.failed_steps]
            colors = ['#10B981', '#EF4444']
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Steps Success Rate')
            
            # Chart 2: Timeline Bar (simulated)
            steps = ['Start', 'Processing', 'Validation', 'Completion']
            times = [0, 30, 70, 100]  # Simulated percentages
            ax2.barh(steps, times, color=['#3B82F6', '#F59E0B', '#8B5CF6', '#10B981'])
            ax2.set_xlabel('Progress %')
            ax2.set_title('Execution Timeline')
            
            # Chart 3: Status Overview
            statuses = ['Total', 'Completed', 'Failed']
            values = [summary.total_steps, summary.completed_steps, summary.failed_steps]
            colors = ['#6B7280', '#10B981', '#EF4444']
            bars = ax3.bar(statuses, values, color=colors)
            ax3.set_title('Step Summary')
            ax3.set_ylabel('Count')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value}', ha='center', va='bottom')
            
            # Chart 4: Performance Metrics
            metrics = ['Duration\n(seconds)', 'Success Rate\n(%)', 'Steps\nCompleted']
            metric_values = [summary.total_duration_seconds, summary.success_rate, summary.completed_steps]
            colors = ['#3B82F6', '#10B981', '#F59E0B']
            
            # Normalize values for display
            normalized_values = [
                summary.total_duration_seconds / 60 if summary.total_duration_seconds > 60 else summary.total_duration_seconds,
                summary.success_rate,
                summary.completed_steps
            ]
            
            bars = ax4.bar(metrics, normalized_values, color=colors)
            ax4.set_title('Key Metrics')
            
            # Add value labels
            for bar, value in zip(bars, metric_values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_bytes = buffer.getvalue()
            buffer.close()
            plt.close()
            
            return chart_bytes
            
        except Exception as e:
            print(f"Error generating analytics chart: {e}")
            return None
    
    async def _generate_daily_analytics_chart(
        self, 
        analytics: WorkflowAnalytics, 
        date_range: Tuple[datetime, datetime]
    ) -> bytes:
        """Generate daily analytics chart"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle(f'Daily Workflow Analytics: {date_range[1].strftime("%Y-%m-%d")}', 
                        fontsize=16, fontweight='bold')
            
            # Chart 1: Success vs Failure
            labels = ['Successful', 'Failed']
            sizes = [analytics.successful_executions, analytics.failed_executions]
            colors = ['#10B981', '#EF4444']
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, 
                                              autopct='%1.1f%%', startangle=90)
            ax1.set_title('Execution Success Rate')
            
            # Chart 2: Performance Trend (simulated)
            if analytics.performance_trend:
                hours = [item.get('hour', i) for i, item in enumerate(analytics.performance_trend)]
                success_rates = [item.get('success_rate', 50 + i*5) for item in analytics.performance_trend]
                ax2.plot(hours, success_rates, marker='o', linewidth=2, markersize=6, color='#3B82F6')
                ax2.set_xlabel('Hour of Day')
                ax2.set_ylabel('Success Rate (%)')
                ax2.set_title('Performance Trend')
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'No trend data available', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=12)
                ax2.set_title('Performance Trend')
            
            # Chart 3: Error Breakdown
            if analytics.error_breakdown:
                error_types = list(analytics.error_breakdown.keys())[:5]  # Top 5
                error_counts = [analytics.error_breakdown[error_type] for error_type in error_types]
                colors = plt.cm.Reds(np.linspace(0.4, 0.8, len(error_types)))
                bars = ax3.barh(error_types, error_counts, color=colors)
                ax3.set_xlabel('Count')
                ax3.set_title('Top Error Types')
                
                # Add value labels
                for bar, count in zip(bars, error_counts):
                    width = bar.get_width()
                    ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                            f'{count}', ha='left', va='center')
            else:
                ax3.text(0.5, 0.5, 'No error data', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=12)
                ax3.set_title('Error Breakdown')
            
            # Chart 4: Overall Metrics
            metrics = ['Total\nExecutions', 'Avg Duration\n(seconds)', 'Success Rate\n(%)']
            values = [analytics.total_executions, analytics.average_execution_time, 
                     analytics.success_rate_percentage]
            colors = ['#6366F1', '#F59E0B', '#10B981']
            
            bars = ax4.bar(metrics, values, color=colors)
            ax4.set_title('Summary Metrics')
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                        f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_bytes = buffer.getvalue()
            buffer.close()
            plt.close()
            
            return chart_bytes
            
        except Exception as e:
            print(f"Error generating daily analytics chart: {e}")
            return None


# Utility functions for data processing
def process_execution_logs_for_report(
    raw_logs: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Process raw execution logs into categorized lists
    Returns: (all_logs, error_logs, warning_logs)
    """
    all_logs = []
    error_logs = []
    warning_logs = []
    
    for log in raw_logs:
        processed_log = {
            'timestamp': log.get('timestamp', datetime.now().isoformat()),
            'level': log.get('level', 'info'),
            'message': log.get('message', ''),
            'node_id': log.get('node_id'),
            'execution_time': log.get('execution_time')
        }
        
        all_logs.append(processed_log)
        
        if processed_log['level'] == 'error':
            error_logs.append(processed_log)
        elif processed_log['level'] == 'warning':
            warning_logs.append(processed_log)
    
    return all_logs, error_logs, warning_logs


def create_execution_summary_from_data(
    workflow_name: str,
    instance_id: str,
    execution_data: Dict[str, Any],
    logs: List[Dict[str, Any]],
    events: List[Dict[str, Any]]
) -> WorkflowExecutionSummary:
    """Create WorkflowExecutionSummary from raw execution data"""
    
    # Parse timestamps and ensure timezone consistency
    start_time = datetime.fromisoformat(execution_data.get('start_time', datetime.now().isoformat()))
    end_time_str = execution_data.get('end_time')
    end_time = datetime.fromisoformat(end_time_str) if end_time_str else None
    
    # Ensure timezone consistency
    from datetime import timezone
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time and end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    
    # Calculate duration
    if end_time:
        duration = (end_time - start_time).total_seconds()
    else:
        now = datetime.now(timezone.utc)
        duration = (now - start_time).total_seconds()
    
    # Process logs for errors and warnings
    _, error_logs, warning_logs = process_execution_logs_for_report(logs)
    
    # Calculate steps
    total_steps = execution_data.get('total_steps', 0)
    completed_steps = execution_data.get('completed_steps', 0)
    failed_steps = execution_data.get('failed_steps', 0)
    
    # Calculate success rate
    success_rate = (completed_steps / total_steps * 100) if total_steps > 0 else 0
    
    return WorkflowExecutionSummary(
        workflow_name=workflow_name,
        instance_id=instance_id,
        status=execution_data.get('status', 'unknown'),
        start_time=start_time,
        end_time=end_time,
        total_duration_seconds=duration,
        total_steps=total_steps,
        completed_steps=completed_steps,
        failed_steps=failed_steps,
        success_rate=success_rate,
        errors=[{'message': log['message'], 'timestamp': log['timestamp']} for log in error_logs],
        warnings=[{'message': log['message'], 'timestamp': log['timestamp']} for log in warning_logs]
    )


# Add required imports
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
