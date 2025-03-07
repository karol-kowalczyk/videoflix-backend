from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    custom = models.CharField(max_length=500, default='')
    phone = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=150, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username als Pflichtfeld hinzufügen!

    def __str__(self):
        return self.email
