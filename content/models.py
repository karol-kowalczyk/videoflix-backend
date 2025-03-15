"""
Model definition for the Video application.

This module defines the Video model, which represents video content stored 
in the application, including metadata such as title, description, and file storage.
"""

from django.db import models
from datetime import date

class Video(models.Model):
    """
    Model representing a video entry.

    This model stores essential metadata about videos, such as the title,
    description, upload date, and the actual video file.
    """
    
    created_at = models.DateField(default=date.today)  
    # Stores the date when the video entry was created, defaults to today's date.
    
    title = models.CharField(max_length=80)  
    # The title of the video, limited to 80 characters.
    
    description = models.CharField(max_length=500)  
    # A brief description of the video, up to 500 characters.
    
    video_file = models.FileField(upload_to='videos', blank=True, null=True)  
    # The video file, stored in the 'videos' directory. Optional field.
    
    is_480p = models.BooleanField(default=False)  
    # Indicates whether a 480p resolution version of the video is available.

    def __str__(self):
        """
        Returns a string representation of the Video instance.

        This method returns the video's title, making it easier to identify
        entries in Django’s admin interface and shell.
        """
        return self.title
