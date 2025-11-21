from django.db import models


class Bus(models.Model):
    """Bus/vehicle information."""
    plate_number = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField()
    company_name = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'buses'
        indexes = [
            models.Index(fields=['plate_number']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.plate_number} ({self.capacity} seats)"

