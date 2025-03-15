from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for creating a new user with the 'CustomUser' model.

    This form extends Django's built-in 'UserCreationForm' and uses the 'CustomUser'
    model. It includes all fields from the 'CustomUser' model for user registration.
    """
    
    class Meta:
        model = CustomUser  # Use the 'CustomUser' model for this form.
        fields = '__all__'  # Include all fields from the 'CustomUser' model in the form.
