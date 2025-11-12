import uuid
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Seat, Ticket


def generate_qr_code():
    return str(uuid.uuid4())


def check_seat_availability(vehicle, date):
    booked_seats = Seat.objects.filter(vehicle=vehicle, is_booked=True).count()
    return booked_seats < vehicle.capacity


def send_ussd_response(phone_number, message):
    print(f"USSD Response to {phone_number}: {message}")


def notify_bus_location(bus_id, location):
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
    try:
        ticket = Ticket.objects.get(qr_code=qr_code)
        if ticket.is_used:
            return {'status': 'error', 'message': 'Ticket already used'}
        ticket.is_used = True
        ticket.validated_at = timezone.now()
        ticket.save()
        return {'status': 'success', 'message': 'Ticket validated'}
    except Ticket.DoesNotExist:
        return {'status': 'error', 'message': 'Invalid ticket'}
