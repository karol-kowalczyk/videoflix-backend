from django.db import models
from datetime import date

class Video(models.Model):
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
    category = models.CharField(
        max_length=3, 
        choices=CATEGORY_CHOICES, 
        default='NEW'
    )

    def __str__(self):
        return self.title


