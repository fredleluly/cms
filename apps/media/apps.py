from django.apps import AppConfig
import os
from django.conf import settings


class MediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.media'
    label = 'media'

    def ready(self):
        # Create necessary directories
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        os.makedirs(settings.MEDIA_ROOT / 'uploads', exist_ok=True)
        os.makedirs(settings.MEDIA_ROOT / 'thumbnails', exist_ok=True)
