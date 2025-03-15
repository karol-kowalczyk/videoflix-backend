"""
Signal handlers for the Video model.

This module defines Django signals to handle automatic video conversion to 480p 
upon creation and to delete associated video files when a Video instance is removed.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
import subprocess
import os

def convert_480p(source):
    """
    Converts a video file to 480p resolution using FFmpeg.

    Args:
        source (str): The file path of the original video.

    Returns:
        str or None: The file path of the converted 480p video if successful, 
                     otherwise None.
    """
    base_name = os.path.splitext(source)[0]
    target = f"{base_name}_480p.mp4"
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return handle_conversion_result(result, target)
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None

def handle_conversion_result(result, target):
    """
    Handles the result of the FFmpeg conversion process.

    Args:
        result (subprocess.CompletedProcess): The result of the FFmpeg command execution.
        target (str): The target file path of the converted video.

    Returns:
        str or None: The target file path if the conversion was successful, otherwise None.
    """
    if result.returncode != 0:
        print(f"Conversion error: {result.stderr}")
        return None
    return target

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for the post-save event of the Video model.

    If a new video is created and it is not a 480p version, 
    it triggers automatic conversion to 480p.

    Args:
        sender (Model class): The model class that triggered the signal.
        instance (Video): The instance of the Video model being saved.
        created (bool): Indicates whether the instance was created (True) or updated (False).
        **kwargs: Additional keyword arguments.
    """
    print('Video saved')

    if created and instance.video_file and not instance.is_480p:
        print('New video created')
        source_path = instance.video_file.path
        target_path = convert_480p(source_path)

        if target_path:
            create_480p_video(instance, target_path)

def create_480p_video(instance, target_path):
    """
    Creates a new Video instance for the 480p version of the original video.

    Args:
        instance (Video): The original video instance.
        target_path (str): The file path of the converted 480p video.
    """
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
    """
    Signal handler for the post-delete event of the Video model.

    Deletes the associated video file when a Video instance is deleted. 
    If the deleted instance is not a 480p version, its 480p counterpart is also removed.

    Args:
        sender (Model class): The model class that triggered the signal.
        instance (Video): The instance of the Video model being deleted.
        **kwargs: Additional keyword arguments.
    """
    if instance.video_file:
        delete_file(instance.video_file.path)

    if not instance.is_480p:
        delete_480p_file(instance)

def delete_file(file_path):
    """
    Deletes a file from the file system.

    Args:
        file_path (str): The file path of the file to be deleted.
    """
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"File deleted: {file_path}")

def delete_480p_file(instance):
    """
    Deletes the 480p version of a video if it exists.

    Args:
        instance (Video): The original video instance.
    """
    base_name = os.path.splitext(instance.video_file.path)[0]
    target_480p = f"{base_name}_480p.mp4"
    
    if os.path.isfile(target_480p):
        os.remove(target_480p)
        print(f"480p file deleted: {target_480p}")
    
    Video.objects.filter(title=f"{instance.title} (480p)", is_480p=True).delete()
