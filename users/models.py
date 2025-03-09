from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    custom = models.CharField(max_length=500, default='')
    phone = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=150, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username als Pflichtfeld hinzufügen!

    def __str__(self):
        return self.email

class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at