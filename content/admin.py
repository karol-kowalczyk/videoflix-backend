from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Video

class VideoResource(resources.ModelResource):
    class Meta:
        model = Video

@admin.register(Video)  # This is enough, no need for admin.site.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    pass

