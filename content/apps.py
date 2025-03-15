"""
App configuration for the Content application.

This module defines the configuration settings for the 'content' app,
including automatic signal registration when the app is ready.
"""

from django.apps import AppConfig

class ContentConfig(AppConfig):
    """
    Configuration class for the 'content' app.

    This class sets the default auto field type and ensures that signal handlers
    are imported when the application is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'

    def ready(self):
        """
        Imports signal handlers when the application is ready.

        This ensures that all signal handlers in 'content.signals' are
        properly registered upon application startup.
        """
        import content.signals  # Import signals to connect them properly
