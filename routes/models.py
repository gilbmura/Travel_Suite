from django.db import models


class District(models.Model):
    """Rwanda districts/locations."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'districts'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class Route(models.Model):
    """Bus routes connecting districts."""
    name = models.CharField(max_length=200)
    origin = models.ForeignKey(District, on_delete=models.CASCADE, related_name='origin_routes')
    destination = models.ForeignKey(District, on_delete=models.CASCADE, related_name='destination_routes')
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_duration_minutes = models.IntegerField(blank=True, null=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00, help_text="Ticket price in RWF")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routes'
        unique_together = [['origin', 'destination']]
        indexes = [
            models.Index(fields=['origin', 'destination']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.origin} → {self.destination})"

