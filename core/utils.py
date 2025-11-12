"""
Utility functions for Travel Suite
"""

import uuid
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from .models import Ticket, Seat


def generate_qr_code():
    """Generate a unique QR code string."""
    return str(uuid.uuid4())


def check_seat_availability(vehicle, date):
    """
    Check if seats are available for a vehicle on a specific date.
    Returns count of available seats.
    """
    booked_seats = Seat.objects.filter(vehicle=vehicle, is_booked=True).count()
    available = vehicle.capacity - booked_seats
    return max(0, available)


def send_ussd_response(phone_number, message):
    """
    Simulate sending USSD response.
    Replace with Africa's Talking API for production.
    """
    print(f"USSD Response to {phone_number}: {message}")
    # Actual implementation would call Africa's Talking API here


def notify_bus_location(bus_id, location):
    """
    Notify all connected clients about bus location via WebSocket.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'bus_locations',
        {
            'type': 'send_location',
            'bus_id': bus_id,
            'location': location,
        }
    )


def validate_ticket(qr_code):
    """
    Validate a ticket using its QR code.
    Returns status dict with success/error message.
    """
    try:
        ticket = Ticket.objects.get(qr_code=qr_code)
        if ticket.is_used:
            return {
                'status': 'error',
                'message': 'Ticket already used',
                'ticket_id': ticket.id
            }
        ticket.is_used = True
        ticket.validated_at = timezone.now()
        ticket.save()
        return {
            'status': 'success',
            'message': 'Ticket validated successfully',
            'ticket_id': ticket.id,
            'booking_id': ticket.booking.id
        }
    except Ticket.DoesNotExist:
        return {
            'status': 'error',
            'message': 'Invalid QR code or ticket not found'
        }
