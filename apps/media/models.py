from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime

User = get_user_model()

def upload_to(instance, filename):
    try:
        # Get the file extension
        ext = filename.split('.')[-1]
        # Create slug from original filename
        filename_slug = slugify(filename.rsplit('.', 1)[0])
        # Use current date instead of instance.uploaded_at
        date_path = datetime.now().strftime("%Y/%m")
        # Get upload path
        upload_path = f'uploads/{instance.content_type}/{date_path}'
        # Create directory if it doesn't exist
        full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
        os.makedirs(full_path, exist_ok=True)
        # Return the complete path
        return f'{upload_path}/{filename_slug}.{ext}'
    except Exception as e:
        print(f"Error in upload_to: {str(e)}")
        return filename

class MediaFile(models.Model):
    CONTENT_TYPES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=upload_to)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    file_size = models.BigIntegerField(editable=False)
    file_extension = models.CharField(max_length=10, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Metadata for images
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Media File'
        verbose_name_plural = 'Media Files'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            # Set file size and extension before saving
            if self.file and not self.pk:  # Only on creation
                self.file_size = self.file.size if hasattr(self.file, 'size') else 0
                self.file_extension = os.path.splitext(self.file.name)[1][1:].lower()

                # Generate thumbnail for images
                if self.content_type == 'image':
                    try:
                        img = Image.open(self.file)
                        self.width = img.width
                        self.height = img.height

                        # Create thumbnail
                        thumb_size = (300, 300)
                        img.thumbnail(thumb_size)
                        thumb_io = BytesIO()
                        img.save(thumb_io, format='JPEG')
                        
                        thumbnail_name = f'thumb_{os.path.basename(self.file.name)}'
                        self.thumbnail.save(
                            thumbnail_name,
                            ContentFile(thumb_io.getvalue()),
                            save=False
                        )
                    except Exception as e:
                        print(f"Error creating thumbnail: {str(e)}")

            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error in save method: {str(e)}")
            raise

    @property
    def file_type_icon(self):
        """Returns the appropriate icon class based on file type"""
        extension = self.file_extension.lower()
        if self.content_type == 'image':
            return 'fa-image'
        elif extension in ['pdf']:
            return 'fa-file-pdf'
        elif extension in ['doc', 'docx']:
            return 'fa-file-word'
        elif extension in ['xls', 'xlsx']:
            return 'fa-file-excel'
        elif self.content_type == 'video':
            return 'fa-video'
        elif self.content_type == 'audio':
            return 'fa-music'
        return 'fa-file'

    @property
    def formatted_file_size(self):
        """Returns human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024
        return f"{self.file_size:.1f} TB"
