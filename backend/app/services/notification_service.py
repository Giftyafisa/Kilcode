from sqlalchemy.orm import Session
from app.models.notification import Notification
from datetime import datetime
from typing import Optional, Dict, Any
import os
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resend configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@kilcode.com")

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """Send an email using Resend"""
    if not RESEND_API_KEY:
        logger.error("Resend API key not configured")
        return False

    # Validate email format
    if not '@' in to_email or not '.' in to_email:
        logger.error(f"Invalid email format: {to_email}")
        return False

    try:
        logger.info(f"Preparing to send email to {to_email}")
        
        # Prepare the request
        headers = {
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Prepare email data
        email_data = {
            "from": SENDER_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": html_content,
        }
        
        if text_content:
            email_data["text"] = text_content
            
        # Send request to Resend API
        response = requests.post(
            'https://api.resend.com/emails',
            headers=headers,
            json=email_data
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('id'):
                logger.info(f"Email sent successfully to {to_email} with ID: {response_data['id']}")
                return True
                
        logger.error(f"Failed to send email: {response.text}")
        return False
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def send_code_purchase_email(
    to_email: str,
    code_details: Dict[str, Any]
) -> bool:
    """Send email notification for purchased code"""
    try:
        # Log the attempt
        logger.info(f"Preparing to send purchase email to {to_email}")
        logger.info(f"Code details: {code_details}")
        
        # Validate code details with more flexible validation
        required_fields = ['code', 'bookmaker', 'win_probability', 'expected_odds', 'valid_until', 'category']
        missing_fields = [field for field in required_fields if not code_details.get(field)]
        
        if missing_fields:
            logger.warning(f"Missing required code details: {', '.join(missing_fields)}")
            logger.warning(f"Received code details: {code_details}")
            # Try to proceed with available data
            for field in missing_fields:
                code_details[field] = 'N/A'
            
        logger.info(f"Sending email for code: {code_details.get('code')}")
        
        # Format valid_until date with better error handling
        valid_until = code_details.get('valid_until')
        if valid_until:
            try:
                if isinstance(valid_until, str):
                    valid_until = datetime.fromisoformat(valid_until).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing valid_until date: {valid_until}, Error: {str(e)}")
                valid_until = str(valid_until)
        else:
            valid_until = 'N/A'
        
        subject = "Your Purchased Betting Code Details"
        
        # Create HTML content
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1a1a1a; color: white; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
                    .code-box {{ background-color: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin: 15px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 0.8em; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Your Betting Code Purchase</h1>
                    </div>
                    <div class="content">
                        <p>Thank you for your purchase! Here are your code details:</p>
                        
                        <div class="code-box">
                            <h3>Code Details:</h3>
                            <p><strong>Code:</strong> {code_details.get('code')}</p>
                            <p><strong>Bookmaker:</strong> {code_details.get('bookmaker')}</p>
                            <p><strong>Win Probability:</strong> {code_details.get('win_probability')}%</p>
                            <p><strong>Expected Odds:</strong> {code_details.get('expected_odds')}</p>
                            <p><strong>Valid Until:</strong> {valid_until}</p>
                            <p><strong>Category:</strong> {code_details.get('category')}</p>
                            {f"<p><strong>Minimum Stake:</strong> {code_details.get('min_stake')}</p>" if code_details.get('min_stake') else ""}
                            {f"<p><strong>Description:</strong> {code_details.get('description')}</p>" if code_details.get('description') else ""}
                        </div>
                        
                        <p><strong>Important Notes:</strong></p>
                        <ul>
                            <li>This code is for your personal use only</li>
                            <li>Please check the validity period before using</li>
                            <li>Make sure to follow the bookmaker's guidelines</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Create plain text content as fallback
        text_content = f"""
        Your Betting Code Purchase

        Thank you for your purchase! Here are your code details:

        Code: {code_details.get('code')}
        Bookmaker: {code_details.get('bookmaker')}
        Win Probability: {code_details.get('win_probability')}%
        Expected Odds: {code_details.get('expected_odds')}
        Valid Until: {valid_until}
        Category: {code_details.get('category')}
        {f"Minimum Stake: {code_details.get('min_stake')}" if code_details.get('min_stake') else ""}
        {f"Description: {code_details.get('description')}" if code_details.get('description') else ""}

        Important Notes:
        - This code is for your personal use only
        - Please check the validity period before using
        - Make sure to follow the bookmaker's guidelines

        This is an automated message, please do not reply to this email.
        """
        
        return send_email(to_email, subject, html_content, text_content)
    except Exception as e:
        logger.error(f"Error preparing email content: {str(e)}")
        logger.error(f"Code details: {code_details}")
        return False

def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    type: str,
    metadata: dict = None
) -> Notification:
    """Create a new notification"""
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            notification_data=metadata,
            read=False,
            created_at=datetime.utcnow()
        )
        print(f"Creating notification: {title} for user {user_id}")  # Debug log
        print(f"Notification data: {metadata}")  # Additional debug log
        return notification
    except Exception as e:
        print(f"Error creating notification: {str(e)}")  # Debug log
        raise 