from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=25, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'auth_user'
