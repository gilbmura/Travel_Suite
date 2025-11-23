"""
Email notification with QR code attachment.
"""
import qrcode
import io
import json
import hashlib
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


def generate_qr_code(booking_id, schedule_id, secret_key=None):
    """
    Generate QR code image for booking.
    
    Args:
        booking_id: Booking UUID
        schedule_id: Schedule occurrence ID
        secret_key: Optional secret key for hash generation
        
    Returns:
        bytes: PNG image bytes
    """
    # Create payload
    payload = {
        'booking_id': str(booking_id),
        'schedule_id': schedule_id,
    }
    
    # Add hash for verification
    if secret_key:
        payload_str = json.dumps(payload, sort_keys=True)
        hash_value = hashlib.sha256(f"{payload_str}{secret_key}".encode()).hexdigest()[:16]
        payload['hash'] = hash_value
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer.getvalue()


def send_booking_email(booking, schedule_occurrence):
    """
    Send booking confirmation email with QR code attachment.
    
    Args:
        booking: Booking instance
        schedule_occurrence: ScheduleOccurrence instance
        
    Returns:
        dict: {
            'success': bool,
            'error': str or None
        }
    """
    if not booking.email:
        return {
            'success': False,
            'error': 'No email address provided'
        }
    
    try:
        # Generate QR code
        qr_image = generate_qr_code(
            booking.id,
            schedule_occurrence.id,
            secret_key=settings.SECRET_KEY
        )
        
        # Prepare email content
        subject = f'Travel Suite - Booking Confirmation {booking.id}'
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=f"""
Dear {booking.passenger_name},

Your booking has been confirmed!

Booking Reference: {booking.id}
Route: {schedule_occurrence.route.name}
Date: {schedule_occurrence.date}
Departure Time: {schedule_occurrence.departure_time}
Phone: {booking.phone_number}

Please find your QR code ticket attached. Present this QR code at the departure point.

Thank you for choosing Travel Suite!

Best regards,
Travel Suite Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        
        # Attach QR code
        email.attach('ticket_qr.png', qr_image, 'image/png')
        
        # Send email
        email.send()
        
        logger.info(f"Booking confirmation email sent to {booking.email} for booking {booking.id}")
        
        return {
            'success': True,
            'error': None
        }
    except Exception as e:
        logger.error(f"Failed to send booking email to {booking.email}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def send_notification_async(booking, schedule_occurrence):
    """
    Async wrapper for sending notifications.
    In MVP, this runs synchronously. In production, connect to Celery or background worker.
    
    Args:
        booking: Booking instance
        schedule_occurrence: ScheduleOccurrence instance
    """
    # TODO: In production, replace with Celery task:
    # from celery import shared_task
    # @shared_task
    # def send_notification_task(booking_id, schedule_id):
    #     ...
    # send_notification_task.delay(booking.id, schedule_occurrence.id)
    
    # MVP: Run synchronously
    from .twilio_client import send_sms
    
    # Send SMS
    sms_message = f"""
Travel Suite Booking Confirmed!

Ref: {booking.id}
Route: {schedule_occurrence.route.name}
Date: {schedule_occurrence.date} {schedule_occurrence.departure_time}

Thank you for choosing Travel Suite!
    """
    send_sms(booking.phone_number, sms_message)
    
    # Send email with QR if email provided
    if booking.email:
        send_booking_email(booking, schedule_occurrence)

