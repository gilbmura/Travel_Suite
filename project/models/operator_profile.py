from django.db import models
from .user import User


class OperatorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operator_profile')
    company_name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f"Operator: {self.company_name}"

    class Meta:
        db_table = 'OperatorProfile'
