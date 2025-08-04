"""
Email Sender Component
Automated email sending component for workflows
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..notifications import EmailService
from ...core.config import settings


@dataclass
class EmailSenderConfig:
    """Configuration for Email Sender component"""
    to_email: str
    subject: str
    body: str
    email_type: str = "html"  # html or plain
    include_attachments: bool = False
    from_name: Optional[str] = None
    
    def validate(self) -> tuple[bool, str]:
        """Validate email configuration"""
        if not self.to_email:
            return False, "Recipient email is required"
        if not self.subject:
            return False, "Email subject is required"
        if not self.body:
            return False, "Email body is required"
        if "@" not in self.to_email:
            return False, "Invalid email format"
        return True, ""


class EmailSenderComponent:
    """
    Automated Email Sender Component for Workflows
    Sends emails automatically during workflow execution
    """
    
    def __init__(self):
        self.component_type = "email"
        self.name = "Email Sender"
        self.description = "Send automated email notifications"
        self.category = "Output & Actions"
        
        # Create email service from settings
        self.email_service = EmailService(
            smtp_server=settings.SMTP_SERVER,
            smtp_port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_USE_TLS
        )
    
    async def execute(
        self,
        input_data: Dict[str, Any],
        config: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute email sending
        
        Args:
            input_data: Data from previous workflow steps
            config: Email component configuration
            context: Workflow context (workflow_name, instance_id, etc.)
        """
        try:
            # Parse configuration
            email_config = EmailSenderConfig(
                to_email=config.get("to_email", ""),
                subject=config.get("subject", ""),
                body=config.get("body", ""),
                email_type=config.get("email_type", "html"),
                include_attachments=config.get("include_attachments", False),
                from_name=config.get("from_name")
            )
            
            # Validate configuration
            is_valid, error_message = email_config.validate()
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Configuration error: {error_message}",
                    "status": "failed"
                }
            
            # Process email content with dynamic data
            processed_subject = self._process_template(email_config.subject, input_data, context)
            processed_body = self._process_template(email_config.body, input_data, context)
            
            # Prepare email data
            email_data = {
                "to_email": email_config.to_email,
                "subject": processed_subject,
                "body": processed_body,
                "from_email": settings.SMTP_FROM_EMAIL,
                "is_html": email_config.email_type == "html"
            }
            
            # Add from name if specified
            if email_config.from_name:
                email_data["from_email"] = f"{email_config.from_name} <{settings.SMTP_FROM_EMAIL}>"
            
            # Add attachments if requested
            if email_config.include_attachments and input_data:
                attachments = self._prepare_attachments(input_data, context)
                if attachments:
                    email_data["attachments"] = attachments
            
            # Send email
            result = await self.email_service.send_email(**email_data)
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": f"Email sent successfully to {email_config.to_email}",
                    "status": "completed",
                    "output_data": {
                        "recipient": email_config.to_email,
                        "subject": processed_subject,
                        "sent_at": datetime.now().isoformat(),
                        "email_type": email_config.email_type
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to send email: {result.get('error', 'Unknown error')}",
                    "status": "failed"
                }
                
        except Exception as e:
            logging.error(f"EmailSenderComponent error: {str(e)}")
            return {
                "success": False,
                "error": f"Email component error: {str(e)}",
                "status": "failed"
            }
    
    def _process_template(
        self, 
        template: str, 
        input_data: Dict[str, Any], 
        context: Dict[str, Any] = None
    ) -> str:
        """
        Process email template with dynamic data
        Supports variables like {input}, {result}, {workflow_name}, etc.
        """
        try:
            processed = template
            
            # Replace input data variables
            if input_data:
                # Replace {input} with entire input data
                if "{input}" in processed:
                    input_str = json.dumps(input_data, indent=2, default=str)
                    processed = processed.replace("{input}", input_str)
                
                # Replace specific input keys like {input.field_name}
                for key, value in input_data.items():
                    placeholder = f"{{input.{key}}}"
                    if placeholder in processed:
                        processed = processed.replace(placeholder, str(value))
                
                # Replace {result} with formatted result
                if "{result}" in processed:
                    result_str = self._format_result_data(input_data)
                    processed = processed.replace("{result}", result_str)
            
            # Replace context variables
            if context:
                for key, value in context.items():
                    placeholder = f"{{{key}}}"
                    if placeholder in processed:
                        processed = processed.replace(placeholder, str(value))
            
            # Replace common variables
            processed = processed.replace("{timestamp}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            processed = processed.replace("{date}", datetime.now().strftime("%Y-%m-%d"))
            processed = processed.replace("{time}", datetime.now().strftime("%H:%M:%S"))
            
            return processed
            
        except Exception as e:
            logging.warning(f"Template processing error: {e}")
            return template
    
    def _format_result_data(self, data: Dict[str, Any]) -> str:
        """Format result data for email display"""
        if not data:
            return "No data available"
        
        try:
            # Create a formatted string of the data
            formatted_lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    formatted_lines.append(f"{key}: {json.dumps(value, indent=2, default=str)}")
                else:
                    formatted_lines.append(f"{key}: {value}")
            
            return "\n".join(formatted_lines)
        except:
            return str(data)
    
    def _prepare_attachments(
        self, 
        input_data: Dict[str, Any], 
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Prepare attachments from workflow data"""
        attachments = []
        
        try:
            # Create JSON attachment with workflow data
            data_json = json.dumps({
                "workflow_data": input_data,
                "context": context or {},
                "generated_at": datetime.now().isoformat()
            }, indent=2, default=str)
            
            filename = f"workflow_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            attachments.append({
                "filename": filename,
                "content": data_json.encode(),
                "content_type": "application/json"
            })
            
        except Exception as e:
            logging.warning(f"Attachment preparation error: {e}")
        
        return attachments
    
    def get_schema(self) -> Dict[str, Any]:
        """Get component configuration schema"""
        return {
            "type": "object",
            "properties": {
                "to_email": {
                    "type": "string",
                    "title": "To Email",
                    "description": "Recipient email address",
                    "format": "email"
                },
                "subject": {
                    "type": "string", 
                    "title": "Subject",
                    "description": "Email subject line"
                },
                "body": {
                    "type": "string",
                    "title": "Email Body",
                    "description": "Email content. Use {input}, {result}, {workflow_name} for dynamic data",
                    "format": "textarea"
                },
                "email_type": {
                    "type": "string",
                    "title": "Email Type",
                    "enum": ["html", "plain"],
                    "default": "html"
                },
                "include_attachments": {
                    "type": "boolean",
                    "title": "Include Attachments",
                    "description": "Include workflow data as JSON attachment",
                    "default": False
                },
                "from_name": {
                    "type": "string",
                    "title": "From Name",
                    "description": "Optional sender name"
                }
            },
            "required": ["to_email", "subject", "body"]
        }
    
    def get_example_config(self) -> Dict[str, Any]:
        """Get example configuration"""
        return {
            "to_email": "user@example.com",
            "subject": "Workflow Completed: {workflow_name}",
            "body": """
            <h2>Workflow Completed Successfully!</h2>
            <p><strong>Workflow:</strong> {workflow_name}</p>
            <p><strong>Completed at:</strong> {timestamp}</p>
            <h3>Results:</h3>
            <pre>{result}</pre>
            """,
            "email_type": "html",
            "include_attachments": True,
            "from_name": "EmbeddedChat Automation"
        }


# Create component instance for registration
email_sender_component = EmailSenderComponent()
