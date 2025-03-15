from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta  

class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django 'User' model.

    This model replaces the default 'username' field with an 'email' field,
    adds additional fields such as 'phone', 'address', and 'custom', and introduces
    an 'is_activated' field to track whether the user has activated their account.
    """
    
    # Fields for custom user attributes
    email = models.EmailField(unique=True)  # Email field, set to be unique
    custom = models.CharField(max_length=500, default='')  # Custom text field for additional user info
    phone = models.CharField(max_length=20, default='')  # Phone number field
    address = models.CharField(max_length=150, default='')  # Address field
    is_activated = models.BooleanField(default=False)  # Flag to check if the user has activated their account

    # Set the username field to 'email' instead of the default 'username'
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']  # Ensure 'username' is required for creating a user (but email will be used for login)

    def __str__(self):
        """
        String representation of the user.

        Returns the user's email as the string representation.
        """
        return self.email

class PasswordResetToken(models.Model):
    """
    Model to store the password reset token for users.

    This model stores a token with an expiration time, and it is used for 
    verifying password reset requests.
    """
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the CustomUser model
    token = models.CharField(max_length=64, unique=True)  # Unique token for password reset
    expires_at = models.DateTimeField()  # Expiration date and time for the token

    def is_valid(self):
        """
        Check if the reset token is still valid.

        A token is valid if the current time is earlier than its expiration time.
        """
        return timezone.now() < self.expires_at

class ActivationToken(models.Model):
    """
    Model to store the account activation token for users.

    This model stores a token with an expiration time for activating a user account.
    """
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to the CustomUser model
    token = models.CharField(max_length=64, unique=True)  # Unique token for account activation
    expires_at = models.DateTimeField()  # Expiration date and time for the token

    def is_valid(self):
        """
        Check if the activation token is still valid.

        A token is valid if the current time is earlier than its expiration time.
        """
        return timezone.now() < self.expires_at
