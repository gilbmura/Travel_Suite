import uuid
from django.db import models
from .booking import Booking


class Ticket(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='ticket')
    qr_code = models.TextField(unique=True)
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
