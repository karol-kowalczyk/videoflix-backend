from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
import subprocess
import os

def convert_480p(source):
    base_name = os.path.splitext(source)[0]
    target = f"{base_name}_480p.mp4"
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return handle_conversion_result(result, target)
    except Exception as e:
        print(f"Fehler bei der Konvertierung: {e}")
        return None

def handle_conversion_result(result, target):
    if result.returncode != 0:
        print(f"Fehler bei der Konvertierung: {result.stderr}")
        return None
    return target

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video save')

    if created and instance.video_file and not instance.is_480p:
        print('New video created')
        source_path = instance.video_file.path
        target_path = convert_480p(source_path)

        if target_path:
            create_480p_video(instance, target_path)

def create_480p_video(instance, target_path):
    relative_path = target_path.replace(f"{instance.video_file.storage.location}/", "")
    Video.objects.create(
        title=f"{instance.title} (480p)",
        description=instance.description,
        video_file=relative_path,
        created_at=instance.created_at,
        is_480p=True
    )

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        delete_file(instance.video_file.path)

    if not instance.is_480p:
        delete_480p_file(instance)

def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"Datei gelöscht: {file_path}")

def delete_480p_file(instance):
    base_name = os.path.splitext(instance.video_file.path)[0]
    target_480p = f"{base_name}_480p.mp4"
    if os.path.isfile(target_480p):
        os.remove(target_480p)
        print(f"480p-Datei gelöscht: {target_480p}")
    Video.objects.filter(title=f"{instance.title} (480p)", is_480p=True).delete()
