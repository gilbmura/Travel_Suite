"""
Utility functions for Travel Suite
"""

import json
import uuid
from decimal import Decimal

from asgiref.sync import async_to_sync
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from channels.layers import get_channel_layer

from .models import (
    Ticket,
    Seat,
    Booking,
    BookingSequence,
    OperatorAssignment,
)


def generate_qr_code():
    """Generate a unique QR code string."""
    return str(uuid.uuid4())


def check_seat_availability(vehicle, travel_date):
    """
    Calculate available seats for a vehicle on a given travel date.
    If travel_date is None, falls back to simple seat count.
    """
    if vehicle is None:
        return 0

    if not travel_date:
        booked_seats = Seat.objects.filter(vehicle=vehicle, is_booked=True).count()
        return max(0, vehicle.capacity - booked_seats)

    confirmed = Booking.objects.filter(
        vehicle=vehicle,
        travel_date=travel_date,
        status='CONFIRMED'
    ).aggregate(total=Sum('seats_booked'))['total'] or 0

    available = vehicle.capacity - confirmed
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


def get_next_booking_id():
    """Generate the next booking identifier in a transaction-safe way."""
    with transaction.atomic():
        sequence, _ = BookingSequence.objects.select_for_update().get_or_create(name='default')
        sequence.last_number += 1
        sequence.save(update_fields=['last_number', 'updated_at'])
        return f"#{sequence.last_number}"


def operator_route_ids(user):
    """Return a list of route IDs assigned to the operator user."""
    if not user or not getattr(user, 'is_operator', False):
        return []
    return list(
        OperatorAssignment.objects.filter(operator__user=user).values_list('route_id', flat=True)
    )
