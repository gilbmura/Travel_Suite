from django.db import models
from .vehicle import Vehicle


class Seat(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10, unique=True)
    is_booked = models.BooleanField(default=False)
    booking = models.ForeignKey('booking.Booking', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.seat_number}"

    class Meta:
        db_table = 'Seat'
