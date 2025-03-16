"""
Admin configuration for the CustomUser model.

This module registers the CustomUser model with the Django admin and customizes its interface.
It uses a custom user creation form and extends the default UserAdmin fieldsets with additional fields.
"""

from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Custom admin class for the CustomUser model.

    This class configures the admin interface for CustomUser by:
      - Using a custom user creation form.
      - Extending the default UserAdmin fieldsets with additional fields ('custom', 'phone', 'address').
    """
    add_form = CustomUserCreationForm
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Individuelle Daten',
            {
                'fields': (
                    'custom',
                    'phone',
                    'address',
                )
            }
        )
    )
