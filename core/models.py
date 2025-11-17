"""
Models for Travel Suite - Core Backend Implementation
Includes: User, Admin, Operator, Customer, Route, Vehicle, Seat, Event, Booking, Ticket, Payment, Transaction
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom User Model with roles for Admin/Operator/Customer."""
    is_admin = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=25, unique=True, blank=True, null=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'auth_user'


class AdminProfile(models.Model):
    """Extended Profile for Admins."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    license_number = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f"Admin: {self.user.username}"

    class Meta:
        db_table = 'AdminProfile'


class OperatorProfile(models.Model):
    """Extended Profile for Operators."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operator_profile')
    company_name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=25, unique=True)
    is_approved = models.BooleanField(default=False, help_text="Admin approval required before operator can log in")

    def __str__(self):
        return f"Operator: {self.company_name}"

    class Meta:
        db_table = 'OperatorProfile'


class OperatorAssignment(models.Model):
    """Mapping between Operators and Routes they manage."""
    operator = models.ForeignKey(OperatorProfile, on_delete=models.CASCADE, related_name='assignments')
    route = models.ForeignKey('Route', on_delete=models.CASCADE, related_name='operator_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operator.company_name} -> {self.route}"

    class Meta:
        db_table = 'OperatorAssignment'
        unique_together = ('operator', 'route')


class Customer(models.Model):
    """Customer Model."""
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=25, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Customer'


class Route(models.Model):
    """Route Model."""
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField(blank=True, null=True)
    stops = models.TextField(blank=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Normalize origin and destination to uppercase for case-insensitive matching."""
        if self.origin:
            self.origin = self.origin.upper()
        if self.destination:
            self.destination = self.destination.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.origin} → {self.destination}"

    class Meta:
        db_table = 'Routes'


class Vehicle(models.Model):
    """Vehicle Model."""
    license_plate = models.CharField(max_length=20, unique=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, db_column='RouteId')
    capacity = models.IntegerField()
    status = models.CharField(
        max_length=12,
        choices=[('Available', 'Available'), ('Unavailable', 'Unavailable')],
        default='Available'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.license_plate

    class Meta:
        db_table = 'Vehicle'


class Seat(models.Model):
    """Seat Model for Vehicle Seat Management."""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    booking = models.ForeignKey('Booking', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.seat_number}"

    class Meta:
        db_table = 'Seat'
        unique_together = ('vehicle', 'seat_number')


class Event(models.Model):
    """Event Model."""
    name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=100)
    available_seats = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Events'


class Booking(models.Model):
    """Booking Model."""
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    booking_id = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, db_column='CustomerId')
    customer_name = models.CharField(max_length=150, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, db_column='EventId')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, db_column='RouteId')
    vehicle = models.ForeignKey('Vehicle', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    seat_number = models.CharField(max_length=20, blank=True)
    seats_booked = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMED')
    travel_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} - {self.customer.name}"

    class Meta:
        db_table = 'Booking'


class Ticket(models.Model):
    """Ticket Model for Validation."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='ticket')
    qr_code = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket for {self.booking}"

    class Meta:
        db_table = 'Ticket'


class Payment(models.Model):
    """Payment Model."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, db_column='BookingId')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=12,
        choices=[('Cash', 'Cash'), ('Card', 'Card'), ('MobileMoney', 'MobileMoney')]
    )
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')],
        default='Pending'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking}"

    class Meta:
        db_table = 'Payments'


class Transaction(models.Model):
    """Transaction Model."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, db_column='Payment_Id')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, db_column='Booking_Id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=10,
        choices=[('Success', 'Success'), ('Failed', 'Failed'), ('Refunded', 'Refunded')],
        default='Success'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for {self.booking}"

    class Meta:
        db_table = 'Transaction'


class BookingSequence(models.Model):
    """Simple sequence table to generate human-friendly booking IDs."""
    name = models.CharField(max_length=50, unique=True, default='default')
    last_number = models.PositiveIntegerField(default=1000)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.last_number}"

    class Meta:
        db_table = 'BookingSequence'
