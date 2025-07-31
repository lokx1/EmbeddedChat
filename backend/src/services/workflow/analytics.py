"""
Analytics and Reporting Service for Workflow
"""
import asyncio
import io
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ...models.workflow import WorkflowTaskLog, WorkflowDailyReport
from .google_services import GoogleDriveService


class AnalyticsService:
    """Service for generating analytics and reports"""
    
    def __init__(self, db_session: Session, google_drive_service: GoogleDriveService = None):
        self.db = db_session
        self.drive_service = google_drive_service
        
        # Set matplotlib backend for server environments
        plt.switch_backend('Agg')
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    async def generate_daily_report(self, report_date: str) -> Dict[str, Any]:
        """Generate daily analytics report"""
        try:
            # Parse date
            date_obj = datetime.strptime(report_date, '%Y-%m-%d')
            start_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # Query task logs for the day
            task_logs = self.db.query(WorkflowTaskLog).filter(
                and_(
                    WorkflowTaskLog.created_at >= start_date,
                    WorkflowTaskLog.created_at < end_date
                )
            ).all()
            
            # Calculate metrics
            total_tasks = len(task_logs)
            successful_tasks = len([log for log in task_logs if log.status == 'success'])
            failed_tasks = len([log for log in task_logs if log.status == 'failed'])
            success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Error breakdown
            error_breakdown = {}
            for log in task_logs:
                if log.status == 'failed' and log.error_message:
                    error_type = self._categorize_error(log.error_message)
                    error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1
            
            # Generate analytics chart
            chart_url = await self._generate_analytics_chart(
                report_date, task_logs, total_tasks, successful_tasks, failed_tasks
            )
            
            report_data = {
                'report_date': report_date,
                'total_tasks': total_tasks,
                'successful_tasks': successful_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': success_rate,
                'error_breakdown': error_breakdown,
                'analytics_chart_url': chart_url,
                'generated_at': datetime.now().isoformat()
            }
            
            # Save to database
            await self._save_daily_report(report_data)
            
            return report_data
            
        except Exception as e:
            raise Exception(f"Failed to generate daily report: {str(e)}")
    
    async def _generate_analytics_chart(
        self, 
        report_date: str, 
        task_logs: List[WorkflowTaskLog],
        total_tasks: int,
        successful_tasks: int,
        failed_tasks: int
    ) -> Optional[str]:
        """Generate analytics chart and upload to Google Drive"""
        try:
            # Create figure with multiple subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'Daily Workflow Analytics - {report_date}', fontsize=16, fontweight='bold')
            
            # 1. Success/Failure Pie Chart
            if total_tasks > 0:
                labels = ['Successful', 'Failed']
                sizes = [successful_tasks, failed_tasks]
                colors = ['#2ecc71', '#e74c3c']
                
                ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax1.set_title('Task Success Rate')
            else:
                ax1.text(0.5, 0.5, 'No tasks executed', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Task Success Rate')
            
            # 2. Hourly Distribution
            if task_logs:
                hours = [log.created_at.hour for log in task_logs]
                ax2.hist(hours, bins=24, alpha=0.7, color='#3498db', edgecolor='black')
                ax2.set_xlabel('Hour of Day')
                ax2.set_ylabel('Number of Tasks')
                ax2.set_title('Hourly Task Distribution')
                ax2.set_xticks(range(0, 24, 2))
            else:
                ax2.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Hourly Task Distribution')
            
            # 3. Processing Time Distribution
            if task_logs:
                processing_times = [log.processing_time_ms / 1000 for log in task_logs if log.processing_time_ms]
                if processing_times:
                    ax3.hist(processing_times, bins=10, alpha=0.7, color='#9b59b6', edgecolor='black')
                    ax3.set_xlabel('Processing Time (seconds)')
                    ax3.set_ylabel('Number of Tasks')
                    ax3.set_title('Processing Time Distribution')
                else:
                    ax3.text(0.5, 0.5, 'No processing time data', ha='center', va='center', transform=ax3.transAxes)
                    ax3.set_title('Processing Time Distribution')
            else:
                ax3.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Processing Time Distribution')
            
            # 4. Output Format Distribution
            if task_logs:
                output_formats = [log.output_format for log in task_logs if log.output_format]
                format_counts = pd.Series(output_formats).value_counts()
                
                if not format_counts.empty:
                    format_counts.plot(kind='bar', ax=ax4, color='#f39c12')
                    ax4.set_xlabel('Output Format')
                    ax4.set_ylabel('Count')
                    ax4.set_title('Output Format Distribution')
                    ax4.tick_params(axis='x', rotation=45)
                else:
                    ax4.text(0.5, 0.5, 'No format data', ha='center', va='center', transform=ax4.transAxes)
                    ax4.set_title('Output Format Distribution')
            else:
                ax4.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Output Format Distribution')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            # Upload to Google Drive if service is available
            if self.drive_service:
                file_name = f"daily_analytics_{report_date}.png"
                upload_result = await self.drive_service.upload_file(
                    buffer.getvalue(),
                    file_name,
                    "image/png"
                )
                return upload_result.get('web_view_link')
            
            # Close the plot
            plt.close(fig)
            
            return None
            
        except Exception as e:
            print(f"Error generating analytics chart: {str(e)}")
            return None
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message into error types"""
        error_message_lower = error_message.lower()
        
        if 'api' in error_message_lower or 'rate limit' in error_message_lower:
            return 'API Error'
        elif 'network' in error_message_lower or 'connection' in error_message_lower:
            return 'Network Error'
        elif 'file' in error_message_lower or 'storage' in error_message_lower:
            return 'File/Storage Error'
        elif 'validation' in error_message_lower or 'invalid' in error_message_lower:
            return 'Validation Error'
        elif 'timeout' in error_message_lower:
            return 'Timeout Error'
        elif 'authentication' in error_message_lower or 'auth' in error_message_lower:
            return 'Authentication Error'
        else:
            return 'Other Error'
    
    async def _save_daily_report(self, report_data: Dict[str, Any]):
        """Save daily report to database"""
        try:
            # Check if report already exists
            existing_report = self.db.query(WorkflowDailyReport).filter(
                WorkflowDailyReport.report_date == report_data['report_date']
            ).first()
            
            if existing_report:
                # Update existing report
                for key, value in report_data.items():
                    if hasattr(existing_report, key):
                        setattr(existing_report, key, value)
            else:
                # Create new report
                report = WorkflowDailyReport(
                    id=f"report_{report_data['report_date']}_{int(datetime.now().timestamp())}",
                    report_date=datetime.strptime(report_data['report_date'], '%Y-%m-%d'),
                    total_tasks=report_data['total_tasks'],
                    successful_tasks=report_data['successful_tasks'],
                    failed_tasks=report_data['failed_tasks'],
                    success_rate=f"{report_data['success_rate']:.1f}%",
                    error_breakdown=report_data['error_breakdown'],
                    analytics_chart_url=report_data.get('analytics_chart_url'),
                    report_sent=False
                )
                self.db.add(report)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to save daily report: {str(e)}")
    
    async def get_weekly_summary(self, end_date: str) -> Dict[str, Any]:
        """Generate weekly summary report"""
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            start_date_obj = end_date_obj - timedelta(days=7)
            
            # Query task logs for the week
            task_logs = self.db.query(WorkflowTaskLog).filter(
                and_(
                    WorkflowTaskLog.created_at >= start_date_obj,
                    WorkflowTaskLog.created_at <= end_date_obj
                )
            ).all()
            
            # Daily breakdown
            daily_stats = {}
            for i in range(7):
                date = start_date_obj + timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                day_logs = [log for log in task_logs if log.created_at.date() == date.date()]
                daily_stats[date_str] = {
                    'total': len(day_logs),
                    'successful': len([log for log in day_logs if log.status == 'success']),
                    'failed': len([log for log in day_logs if log.status == 'failed'])
                }
            
            # Overall stats
            total_tasks = len(task_logs)
            successful_tasks = len([log for log in task_logs if log.status == 'success'])
            failed_tasks = len([log for log in task_logs if log.status == 'failed'])
            
            return {
                'period': f"{start_date_obj.strftime('%Y-%m-%d')} to {end_date}",
                'total_tasks': total_tasks,
                'successful_tasks': successful_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                'daily_breakdown': daily_stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate weekly summary: {str(e)}")
    
    async def get_model_performance_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get performance statistics by AI model"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            task_logs = self.db.query(WorkflowTaskLog).filter(
                WorkflowTaskLog.created_at >= cutoff_date
            ).all()
            
            model_stats = {}
            for log in task_logs:
                model = log.model_specification
                if model not in model_stats:
                    model_stats[model] = {
                        'total': 0,
                        'successful': 0,
                        'failed': 0,
                        'avg_processing_time': 0,
                        'processing_times': []
                    }
                
                model_stats[model]['total'] += 1
                if log.status == 'success':
                    model_stats[model]['successful'] += 1
                else:
                    model_stats[model]['failed'] += 1
                
                if log.processing_time_ms:
                    model_stats[model]['processing_times'].append(log.processing_time_ms)
            
            # Calculate averages
            for model, stats in model_stats.items():
                if stats['processing_times']:
                    stats['avg_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])
                stats['success_rate'] = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
                del stats['processing_times']  # Remove raw data
            
            return {
                'period_days': days,
                'model_statistics': model_stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to get model performance stats: {str(e)}")
    
    async def export_data_to_excel(self, start_date: str, end_date: str) -> bytes:
        """Export workflow data to Excel file"""
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Query data
            task_logs = self.db.query(WorkflowTaskLog).filter(
                and_(
                    WorkflowTaskLog.created_at >= start_date_obj,
                    WorkflowTaskLog.created_at <= end_date_obj
                )
            ).all()
            
            # Convert to DataFrame
            data = []
            for log in task_logs:
                data.append({
                    'Task ID': log.task_id,
                    'Sheet ID': log.sheet_id,
                    'Row Number': log.row_number,
                    'Description': log.input_description,
                    'Output Format': log.output_format,
                    'Model': log.model_specification,
                    'Status': log.status,
                    'Processing Time (ms)': log.processing_time_ms,
                    'Error Message': log.error_message,
                    'Created At': log.created_at,
                    'Completed At': log.completed_at
                })
            
            df = pd.DataFrame(data)
            
            # Create Excel file in memory
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Task Logs', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Total Tasks', 'Successful Tasks', 'Failed Tasks', 'Success Rate (%)'],
                    'Value': [
                        len(task_logs),
                        len([log for log in task_logs if log.status == 'success']),
                        len([log for log in task_logs if log.status == 'failed']),
                        (len([log for log in task_logs if log.status == 'success']) / len(task_logs) * 100) if task_logs else 0
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to export data to Excel: {str(e)}")
