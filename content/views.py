"""
Views for the Video application.

This module defines views for handling Video model data, including API endpoints 
and caching functionality to optimize performance.
"""

from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from .models import Video
from .serializers import VideoSerializer
from rest_framework import viewsets

# Cache timeout duration, retrieved from Django settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

@cache_page(CACHE_TTL)
def recipes_view(request):
    """
    Renders the recipes page with cached content.

    This view caches the rendered HTML page for improved performance.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML response with cached recipe data.
    """
    return render(request, 'cookbook/recipes.html', {
        'recipes': get_recipes()  # Ensure get_recipes() is defined elsewhere
    })

class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Video instances.

    This viewset provides standard CRUD operations for the Video model using Django REST framework.
    """
    queryset = Video.objects.all()  # Retrieves all Video objects from the database
    serializer_class = VideoSerializer  # Specifies the serializer for the Video model
