import uuid
from django.db import models
from django.utils import timezone
from buses.models import Bus
from routes.models import Route


class ScheduleRecurrence(models.Model):
    """Recurring schedule rules."""
    RECURRENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedule_recurrences')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedule_recurrences')
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='daily')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedule_recurrences'
        indexes = [
            models.Index(fields=['route', 'is_active']),
            models.Index(fields=['departure_time']),
        ]
    
    def __str__(self):
        return f"{self.route} - {self.departure_time} ({self.recurrence_type})"


class ScheduleOccurrence(models.Model):
    """Concrete schedule occurrence (specific trip on a date)."""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('departed', 'Departed'),
        ('cancelled', 'Cancelled'),
    ]
    
    recurrence = models.ForeignKey(ScheduleRecurrence, on_delete=models.CASCADE, related_name='occurrences')
    date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedule_occurrences'
        unique_together = [['recurrence', 'date']]
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['recurrence', 'date']),
            models.Index(fields=['departure_time', 'date']),
        ]
    
    @property
    def bus(self):
        return self.recurrence.bus
    
    @property
    def route(self):
        return self.recurrence.route
    
    @property
    def capacity(self):
        return self.recurrence.bus.capacity
    
    @property
    def remaining_seats(self):
        """Calculate remaining seats in real-time."""
        confirmed_count = self.bookings.filter(status='confirmed').count()
        return max(0, self.capacity - confirmed_count)
    
    @property
    def time_to_departure(self):
        """Calculate time remaining until departure."""
        if self.status == 'departed':
            return None
        now = timezone.now()
        departure_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.departure_time)
        )
        if departure_datetime <= now:
            return None
        delta = departure_datetime - now
        return int(delta.total_seconds() / 60)  # minutes
    
    def __str__(self):
        return f"{self.recurrence.route} - {self.date} {self.departure_time}"


class Booking(models.Model):
    """Passenger booking."""
    PAYMENT_METHOD_CHOICES = [
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
        ('cash', 'Cash'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passenger_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    schedule_occurrence = models.ForeignKey(ScheduleOccurrence, on_delete=models.CASCADE, related_name='bookings')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    refund_id = models.CharField(max_length=100, blank=True, null=True)
    operator = models.ForeignKey('operators.OperatorUser', on_delete=models.SET_NULL, blank=True, null=True, related_name='bookings')
    
    class Meta:
        db_table = 'bookings'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
            models.Index(fields=['schedule_occurrence', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.passenger_name} - {self.schedule_occurrence} ({self.status})"
    
    def can_cancel(self):
        """Check if booking can be cancelled."""
        if self.status not in ['pending', 'confirmed']:
            return False
        if self.schedule_occurrence.status == 'departed':
            return False
        return True
    
    def can_refund(self):
        """Check if booking is eligible for auto-refund (>1 hour before departure)."""
        if not self.can_cancel():
            return False
        time_to_departure = self.schedule_occurrence.time_to_departure
        if time_to_departure is None:
            return False
        return time_to_departure > 60  # More than 1 hour (60 minutes)

