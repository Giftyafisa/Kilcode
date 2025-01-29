import logging
from typing import Optional
import os
from app.services.notification_service import send_email as notification_send_email

logger = logging.getLogger(__name__)

async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using the notification service.
    """
    try:
        return notification_send_email(to_email, subject, html_content, text_content)
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        return False

async def send_reset_password_email(email: str, reset_token: str) -> bool:
    """
    Send password reset email.
    """
    # Get frontend URL from environment variable
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Construct the reset URL using the token
    reset_url = f"{frontend_url}/reset-password?token={reset_token}"
    
    subject = "Reset Your Password"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Reset Your Password</h2>
                <p>Hello,</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                <p>If you didn't request this password reset, you can safely ignore this email.</p>
                <p>This link will expire in 24 hours.</p>
                <p>Best regards,<br>Your Support Team</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    If the button above doesn't work, copy and paste this link into your browser:<br>
                    <a href="{reset_url}" style="color: #2563eb;">{reset_url}</a>
                </p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    Reset Your Password

    Hello,

    We received a request to reset your password. Click the link below to create a new password:

    {reset_url}

    If you didn't request this password reset, you can safely ignore this email.

    This link will expire in 24 hours.

    Best regards,
    Your Support Team
    """
    
    return await send_email(email, subject, html_content, text_content) 