"""
Admin configuration for the Video model.

This module defines the Django admin interface for managing Video instances,
including import and export functionality using django-import-export.
"""

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Video

class VideoResource(resources.ModelResource):
    """
    Resource class for the Video model.

    This class enables data import and export functionality for Video instances
    within the Django admin panel.
    """
    class Meta:
        model = Video  # Associates the resource with the Video model
