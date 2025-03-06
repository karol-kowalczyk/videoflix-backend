from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
import subprocess
import os

# Video-Konvertierung in 480p
def convert_480p(source):
    base_name = os.path.splitext(source)[0]
    target = f"{base_name}_480p.mp4"
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    subprocess.run(cmd, shell=True)

# Video speichern: Konvertierung auslösen
@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video save')
    if created and instance.video_file:
        print('New video created')
        convert_480p(instance.video_file.path)

# Video löschen: Datei entfernen
@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        file_path = instance.video_file.path
        if os.path.isfile(file_path):
            os.remove(file_path)
