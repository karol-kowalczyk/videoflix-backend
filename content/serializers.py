"""
Serializers for the Video application.

This module defines the VideoSerializer which is used by the Django REST framework
to serialize and deserialize Video model instances. It converts Video objects into JSON format
and vice versa for API operations.
"""

from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model.

    This serializer handles the conversion between Video model instances and their JSON representations.
    It includes the following fields:
      - id: The unique identifier for the video.
      - created_at: The date the video was created.
      - title: The title of the video.
      - description: A brief description of the video.
      - video_file: The associated video file.
      - category: The category of the video, chosen from predefined options.
    """
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'video_file', 'category']
