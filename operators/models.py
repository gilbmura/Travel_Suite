from django.db import models
from django.conf import settings
from routes.models import Route


class OperatorUser(models.Model):
    """Operator user profile."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='operator_profile')
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'operator_users'
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.user.username})"


class OperatorAssignment(models.Model):
    """Operator route/schedule assignments."""
    operator = models.ForeignKey(OperatorUser, on_delete=models.CASCADE, related_name='assignments')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='operator_assignments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'operator_assignments'
        unique_together = [['operator', 'route']]
        indexes = [
            models.Index(fields=['operator', 'is_active']),
            models.Index(fields=['route']),
        ]
    
    def __str__(self):
        return f"{self.operator.full_name} → {self.route.name}"

