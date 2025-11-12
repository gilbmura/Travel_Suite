from django.db import models
from .user import User


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    license_number = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f"Admin: {self.user.username}"

    class Meta:
        db_table = 'AdminProfile'
