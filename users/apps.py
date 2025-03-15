from django.apps import AppConfig

class UsersConfig(AppConfig):
    """
    Configuration for the 'users' application in the Django project.

    This class defines the configuration for the 'users' app, including setting
    the default primary key field type to 'BigAutoField' and specifying the app's name.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # Set the default field type for auto-incrementing primary keys.
    name = 'users'  # Define the app's name for Django's app registry.
