"""
Email Configuration Settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import EmailStr


class EmailSettings(BaseSettings):
    """Email configuration settings"""
    
    # SMTP Server Configuration
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    
    # Authentication
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    
    # From Address
    smtp_from_email: EmailStr = os.getenv("SMTP_FROM_EMAIL", "noreply@example.com")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "EmbeddedChat System")
    
    # Email Templates
    template_dir: str = os.getenv("EMAIL_TEMPLATE_DIR", "templates/email")
    
    # Email Settings
    default_timeout: int = int(os.getenv("EMAIL_TIMEOUT", "30"))
    max_retries: int = int(os.getenv("EMAIL_MAX_RETRIES", "3"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate_config(self) -> bool:
        """Validate email configuration"""
        required_fields = [
            self.smtp_server,
            self.smtp_username,
            self.smtp_password,
            self.smtp_from_email
        ]
        
        if not all(required_fields):
            return False
            
        return True
    
    def get_smtp_config(self) -> dict:
        """Get SMTP configuration as dictionary"""
        return {
            "hostname": self.smtp_server,
            "port": self.smtp_port,
            "use_tls": self.smtp_use_tls,
            "username": self.smtp_username,
            "password": self.smtp_password,
            "timeout": self.default_timeout
        }


# Global email settings instance
email_settings = EmailSettings()
