from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video save')
    if created:
        print('New video created')

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        file_path = instance.video_file.path
        if os.path.isfile(file_path):
            os.remove(file_path)
