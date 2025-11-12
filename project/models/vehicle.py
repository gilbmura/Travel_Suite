from django.db import models
from .route import Route


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable')
    ]

    license_plate = models.CharField(max_length=20, unique=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, db_column='RouteId')
    capacity = models.IntegerField()
    available_seats = models.IntegerField(default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.license_plate

    class Meta:
        db_table = 'Vehicle'
