from django.db import models
from .payment import Payment
from .booking import Booking


class Transaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded')
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, db_column='Payment_Id')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, db_column='Booking_Id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Success')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for {self.booking}"

    class Meta:
        db_table = 'Transaction'
