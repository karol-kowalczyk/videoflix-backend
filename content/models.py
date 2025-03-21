"""
Models for the Video application.

This module defines the Video model which represents a video item in the application.
Each Video instance includes metadata such as creation date, title, description, the associated video file,
and a category selected from a predefined set of choices.
"""

from django.db import models
from datetime import date

class Video(models.Model):
    """
    Represents a video in the Videoflix application.

    Attributes:
        CATEGORY_CHOICES (list): A list of tuples defining available video categories.
        created_at (DateField): The date when the video was created, defaulting to the current date.
        title (CharField): The title of the video.
        description (CharField): A short description of the video.
        video_file (FileField): The video file stored in the 'videos' directory; may be empty.
        is_480p (BooleanField): Indicates whether the video is a 480p version.
        category (CharField): The category of the video, chosen from CATEGORY_CHOICES.
    """
    CATEGORY_CHOICES = [
        ('NEW', 'New on Videoflix'),
        ('DOC', 'Documentary'),
        ('DRA', 'Drama'),
        ('ROM', 'Romance'),
    ]
    
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    is_480p = models.BooleanField(default=False)
    category = models.CharField(
        max_length=3, 
        choices=CATEGORY_CHOICES, 
        default='NEW'
    )

    def __str__(self):
        """
        Returns a string representation of the Video instance.
        """
        return self.title
