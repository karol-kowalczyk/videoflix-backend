"""
Signal handlers for the Video model.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
import os

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video saved')

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.video_file and instance.video_file.name:
            file_path = instance.video_file.path
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File deleted: {file_path}")
    except ValueError as e:
        print(f"No file associated with video_file: {e}")
