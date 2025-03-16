"""
Signal handlers for the Video model.

This module defines signal handlers that are triggered on save and delete events of Video instances.
On save, a simple log message is printed.
On delete, the associated video file is removed from the filesystem if it exists.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
import os

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Handles the post-save signal for Video instances.

    When a Video instance is saved (created or updated), this function is called.
    Currently, it simply prints a log message to indicate that a video was saved.
    
    Args:
        sender (Model class): The model class that sent the signal (Video).
        instance (Video): The Video instance that was saved.
        created (bool): True if the instance was created, False if updated.
        **kwargs: Additional keyword arguments.
    """
    print('Video saved')

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Handles the post-delete signal for Video instances.

    When a Video instance is deleted, this function checks if the instance has an associated
    video file. If the file exists on the filesystem, it is removed to free up storage space.
    
    Args:
        sender (Model class): The model class that sent the signal (Video).
        instance (Video): The Video instance that was deleted.
        **kwargs: Additional keyword arguments.
    """
    try:
        # Check if there is a file associated with the video_file field
        if instance.video_file and instance.video_file.name:
            file_path = instance.video_file.path  # Get the file system path of the video file
            if os.path.isfile(file_path):         # Verify that the file exists
                os.remove(file_path)              # Delete the file
                print(f"File deleted: {file_path}")
    except ValueError as e:
        # If there is no file associated, a ValueError might be raised; log the error message
        print(f"No file associated with video_file: {e}")
