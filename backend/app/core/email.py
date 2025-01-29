import os
import logging
import resend  # Direct import
from fastapi import HTTPException
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        if not self.api_key:
            logger.error("Resend API key not configured")
            raise ValueError("Resend API key not configured")
            
        resend.api_key = self.api_key  # Set API key directly
        self.from_email = os.getenv("SENDER_EMAIL", "noreply@kilcode.com")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ):
        """Send an email using Resend with better error handling"""
        try:
            # Validate email format
            if not '@' in to_email or not '.' in to_email:
                logger.error(f"Invalid email format: {to_email}")
                raise ValueError(f"Invalid email format: {to_email}")

            logger.info(f"Sending email to {to_email}")
            
            email_data = {
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content,
            }
            
            if text_content:
                email_data["text"] = text_content

            response = resend.Emails.send(email_data)
            
            if response and response.get('id'):
                logger.info(f"Email sent successfully to {to_email} with ID: {response['id']}")
                return response
            
            logger.error(f"Failed to send email: {response}")
            raise HTTPException(status_code=500, detail="Failed to send email")
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

email_service = EmailService() 