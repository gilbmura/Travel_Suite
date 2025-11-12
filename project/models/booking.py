from django.db import models
from .customer import Customer
from .event import Event
from .route import Route


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='CustomerId')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, db_column='EventId')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, db_column='RouteId')
    seat_number = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} - {self.customer.name}"

    class Meta:
        db_table = 'Booking'
