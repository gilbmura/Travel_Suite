"""
Twilio SMS client for sending notifications.
In MVP, uses placeholder credentials. Replace with actual Twilio credentials for production.
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_sms(phone_number, message):
    """
    Send SMS via Twilio.
    
    Args:
        phone_number: Recipient phone number (E.164 format)
        message: SMS message text
        
    Returns:
        dict: {
            'success': bool,
            'message_sid': str or None,
            'error': str or None
        }
    """
    try:
        # Check if Twilio credentials are configured
        if not all([settings.TWILIO_SID, settings.TWILIO_TOKEN, settings.TWILIO_FROM]):
            logger.warning("Twilio credentials not configured. SMS not sent.")
            return {
                'success': False,
                'message_sid': None,
                'error': 'Twilio credentials not configured'
            }
        
        # Import Twilio client
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        
        message_obj = client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM,
            to=phone_number
        )
        
        logger.info(f"SMS sent successfully to {phone_number}. SID: {message_obj.sid}")
        
        return {
            'success': True,
            'message_sid': message_obj.sid,
            'error': None
        }
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return {
            'success': False,
            'message_sid': None,
            'error': str(e)
        }

