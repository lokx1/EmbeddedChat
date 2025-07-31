"""
Notification Services for Workflow
"""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(
        self, 
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str = None,
        attachments: List[Dict[str, Any]] = None,
        is_html: bool = False
    ) -> Dict[str, Any]:
        """Send an email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = from_email or self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    await self._add_attachment(msg, attachment)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(from_email or self.username, to_email, text)
            server.quit()
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            filename = attachment.get('filename')
            content = attachment.get('content')  # bytes
            mime_type = attachment.get('mime_type', 'application/octet-stream')
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
            
        except Exception as e:
            print(f"Warning: Could not add attachment {attachment.get('filename')}: {str(e)}")
    
    async def send_workflow_completion_email(
        self,
        to_email: str,
        workflow_name: str,
        status: str,
        summary: Dict[str, Any],
        output_files: List[str] = None
    ) -> Dict[str, Any]:
        """Send workflow completion notification email"""
        subject = f"Workflow {status.title()}: {workflow_name}"
        
        if status == "completed":
            body = f"""
            <html>
            <body>
                <h2>Workflow Completed Successfully</h2>
                <p><strong>Workflow:</strong> {workflow_name}</p>
                <p><strong>Status:</strong> {status.title()}</p>
                <p><strong>Completion Time:</strong> {summary.get('updated_at', 'N/A')}</p>
                
                <h3>Summary:</h3>
                <ul>
                    <li>Total Steps: {summary.get('total_steps', 0)}</li>
                    <li>Completed Steps: {summary.get('completed_steps', 0)}</li>
                    <li>Success Rate: {summary.get('success_rate', 0):.1f}%</li>
                    <li>Generated Files: {summary.get('generated_files_count', 0)}</li>
                    <li>Notifications Sent: {summary.get('notifications_sent_count', 0)}</li>
                </ul>
            """
                
            # Add output files section if present
            if output_files:
                body += "<h3>Output Files:</h3><ul>"
                for url in output_files:
                    body += f'<li><a href="{url}">{url}</a></li>'
                body += "</ul>"
            
            body += """
                <p>Best regards,<br>Workflow Automation System</p>
            </body>
            </html>
            """
        else:
            body = f"""
            <html>
            <body>
                <h2>Workflow Failed</h2>
                <p><strong>Workflow:</strong> {workflow_name}</p>
                <p><strong>Status:</strong> {status.title()}</p>
                <p><strong>Failure Time:</strong> {summary.get('updated_at', 'N/A')}</p>
                
                <h3>Summary:</h3>
                <ul>
                    <li>Total Steps: {summary.get('total_steps', 0)}</li>
                    <li>Completed Steps: {summary.get('completed_steps', 0)}</li>
                    <li>Failed Steps: {summary.get('failed_steps', 0)}</li>
                    <li>Errors: {summary.get('errors_count', 0)}</li>
                </ul>
                
                <p>Please check the workflow logs for more details.</p>
                
                <p>Best regards,<br>Workflow Automation System</p>
            </body>
            </html>
            """
        
        return await self.send_email(to_email, subject, body, is_html=True)


class SlackService:
    """Service for sending Slack notifications"""
    
    def __init__(self, bot_token: str, default_channel: str = None):
        self.client = AsyncWebClient(token=bot_token)
        self.default_channel = default_channel
    
    async def send_message(
        self,
        message: str,
        channel: str = None,
        thread_ts: str = None,
        blocks: List[Dict] = None
    ) -> Dict[str, Any]:
        """Send a Slack message"""
        try:
            channel = channel or self.default_channel
            
            response = await self.client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=thread_ts,
                blocks=blocks
            )
            
            return {
                "success": True,
                "message": "Slack message sent successfully",
                "timestamp": response["ts"],
                "channel": response["channel"]
            }
            
        except SlackApiError as e:
            return {
                "success": False,
                "error": f"Slack API Error: {e.response['error']}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def send_workflow_notification(
        self,
        workflow_name: str,
        status: str,
        summary: Dict[str, Any],
        channel: str = None
    ) -> Dict[str, Any]:
        """Send workflow completion notification to Slack"""
        
        if status == "completed":
            color = "good"
            emoji = "✅"
            title = "Workflow Completed Successfully"
        else:
            color = "danger"
            emoji = "❌"
            title = "Workflow Failed"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {title}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Workflow:*\n{workflow_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status.title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Steps:*\n{summary.get('total_steps', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Completed Steps:*\n{summary.get('completed_steps', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Success Rate:*\n{summary.get('success_rate', 0):.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Generated Files:*\n{summary.get('generated_files_count', 0)}"
                    }
                ]
            }
        ]
        
        if status != "completed" and summary.get('errors_count', 0) > 0:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Errors:* {summary.get('errors_count', 0)} errors occurred during execution."
                }
            })
        
        return await self.send_message("", channel=channel, blocks=blocks)
    
    async def send_daily_report(
        self,
        report_data: Dict[str, Any],
        chart_url: str = None,
        channel: str = None
    ) -> Dict[str, Any]:
        """Send daily analytics report to Slack"""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Daily Workflow Report - {report_data['report_date']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Tasks:*\n{report_data['total_tasks']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Successful:*\n{report_data['successful_tasks']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n{report_data['failed_tasks']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Success Rate:*\n{report_data['success_rate']:.1f}%"
                    }
                ]
            }
        ]
        
        if report_data.get('error_breakdown'):
            error_text = "\n".join([f"• {error_type}: {count}" for error_type, count in report_data['error_breakdown'].items()])
            newline = "\n"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Breakdown:*{newline}{error_text}"
                }
            })
        
        if chart_url:
            blocks.append({
                "type": "image",
                "image_url": chart_url,
                "alt_text": "Daily Analytics Chart"
            })
        
        return await self.send_message("", channel=channel, blocks=blocks)


class NotificationManager:
    """Manager for all notification services"""
    
    def __init__(
        self,
        email_service: EmailService = None,
        slack_service: SlackService = None
    ):
        self.email_service = email_service
        self.slack_service = slack_service
    
    async def send_workflow_completion_notification(
        self,
        workflow_name: str,
        status: str,
        summary: Dict[str, Any],
        email_recipients: List[str] = None,
        slack_channel: str = None,
        output_files: List[str] = None
    ) -> Dict[str, Any]:
        """Send completion notifications via all configured channels"""
        
        results = {
            "email_results": [],
            "slack_results": []
        }
        
        # Send email notifications
        if self.email_service and email_recipients:
            for email in email_recipients:
                result = await self.email_service.send_workflow_completion_email(
                    email, workflow_name, status, summary, output_files
                )
                results["email_results"].append({
                    "recipient": email,
                    **result
                })
        
        # Send Slack notification
        if self.slack_service:
            result = await self.slack_service.send_workflow_notification(
                workflow_name, status, summary, slack_channel
            )
            results["slack_results"].append(result)
        
        return results
    
    async def send_daily_report_notification(
        self,
        report_data: Dict[str, Any],
        chart_url: str = None,
        email_recipients: List[str] = None,
        slack_channel: str = None
    ) -> Dict[str, Any]:
        """Send daily report notifications"""
        
        results = {
            "email_results": [],
            "slack_results": []
        }
        
        # Send email notifications
        if self.email_service and email_recipients:
            subject = f"Daily Workflow Report - {report_data['report_date']}"
            body = self._generate_daily_report_email_body(report_data, chart_url)
            
            for email in email_recipients:
                result = await self.email_service.send_email(
                    email, subject, body, is_html=True
                )
                results["email_results"].append({
                    "recipient": email,
                    **result
                })
        
        # Send Slack notification
        if self.slack_service:
            result = await self.slack_service.send_daily_report(
                report_data, chart_url, slack_channel
            )
            results["slack_results"].append(result)
        
        return results
    
    def _generate_daily_report_email_body(self, report_data: Dict[str, Any], chart_url: str = None) -> str:
        """Generate HTML email body for daily report"""
        
        error_breakdown_html = ""
        if report_data.get('error_breakdown'):
            error_items = "".join([f"<li>{error_type}: {count}</li>" for error_type, count in report_data['error_breakdown'].items()])
            error_breakdown_html = f"<h3>Error Breakdown:</h3><ul>{error_items}</ul>"
        
        chart_html = ""
        if chart_url:
            chart_html = f'<h3>Analytics Chart:</h3><img src="{chart_url}" alt="Daily Analytics Chart" style="max-width: 100%; height: auto;">'
        
        return f"""
        <html>
        <body>
            <h2>📊 Daily Workflow Report - {report_data['report_date']}</h2>
            
            <h3>Summary:</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Total Tasks</strong></td><td>{report_data['total_tasks']}</td></tr>
                <tr><td><strong>Successful Tasks</strong></td><td>{report_data['successful_tasks']}</td></tr>
                <tr><td><strong>Failed Tasks</strong></td><td>{report_data['failed_tasks']}</td></tr>
                <tr><td><strong>Success Rate</strong></td><td>{report_data['success_rate']:.1f}%</td></tr>
            </table>
            
            {error_breakdown_html}
            {chart_html}
            
            <p>Best regards,<br>Workflow Automation System</p>
        </body>
        </html>
        """
