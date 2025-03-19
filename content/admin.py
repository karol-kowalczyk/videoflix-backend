"""
Admin configuration for the Video model.

This module defines a ModelResource for the Video model to facilitate data
import and export operations using the django-import-export package, and also
registers a custom admin interface for managing Video instances.
"""

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Video

class VideoResource(resources.ModelResource):
    """
    ModelResource for the Video model.

    This class provides configuration for importing and exporting Video data.
    It uses the Video model as the basis for data serialization/deserialization.
    """
    class Meta:
        model = Video

@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    """
    Custom admin interface for the Video model.

    Inherits from ImportExportModelAdmin to enable data import/export features.
    The list_display attribute specifies the model fields to display in the admin list view.
    """
    list_display = ['title', 'category', 'created_at']
