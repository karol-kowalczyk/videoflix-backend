"""
Serializer definition for the Video model.

This module defines a serializer to convert Video model instances into JSON format,
making them suitable for API responses and data exchange.
"""

from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model.

    This serializer converts Video model instances into JSON format and 
    ensures that only the specified fields are included in the API response.
    """

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'video_file', 'category']
        