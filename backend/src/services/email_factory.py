"""
Email Service Factory
Creates EmailService instance from application settings
"""
from services.workflow.notifications import EmailService
from core.config import settings


def create_email_service() -> EmailService:
    """Create EmailService instance from application settings"""
    return EmailService(
        smtp_server=settings.SMTP_SERVER,
        smtp_port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        use_tls=settings.SMTP_USE_TLS
    )


def create_email_report_service():
    """Create EmailReportService with proper dependencies"""
    from services.workflow.email_report_service import EmailReportService
    email_service = create_email_service()
    return EmailReportService(email_service)
