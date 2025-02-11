from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Constants for image optimization
WEBP_QUALITY = 85
JPEG_QUALITY = 85
MAX_WIDTH = 1920
THUMBNAIL_SIZE = (300, 300)
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'GIF', 'WEBP'}

User = get_user_model()

def upload_to(instance, filename):
    """
    Generates upload path with proper organization and slug-based filenames
    """
    try:
        # Get the file extension
        ext = filename.split('.')[-1].lower()
        # Create slug from original filename
        filename_slug = slugify(filename.rsplit('.', 1)[0])
        # Use current date for organization
        date_path = datetime.now().strftime("%Y/%m")
        # Get upload path
        upload_path = f'uploads/{instance.content_type}/{date_path}'
        # Create directory if it doesn't exist
        full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
        os.makedirs(full_path, exist_ok=True)
        # Return the complete path
        return f'{upload_path}/{filename_slug}.{ext}'
    except Exception as e:
        logger.error(f"Error in upload_to for file {filename}: {str(e)}")
        return filename

def optimize_image(img, max_width=MAX_WIDTH, convert_to_webp=True):
    """
    Optimize image by:
    1. Converting to WebP format
    2. Resizing if too large
    3. Optimizing quality
    4. Converting RGBA to RGB
    """
    try:
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background

        # Resize if width exceeds max_width
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        return img
    except Exception as e:
        logger.error(f"Error optimizing image: {str(e)}")
        return None

def create_thumbnail(img, size=THUMBNAIL_SIZE):
    """Create optimized thumbnail in WebP format"""
    try:
        # Create a copy to avoid modifying original
        thumb = img.copy()
        thumb.thumbnail(size)
        
        # Convert to WebP format
        thumb_io = BytesIO()
        thumb.save(thumb_io, format='WEBP', quality=WEBP_QUALITY)
        return thumb_io.getvalue()
    except Exception as e:
        logger.error(f"Error creating thumbnail: {str(e)}")
        return None

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
        """
        Enhanced save method with:
        1. WebP conversion
        2. Proper error handling
        3. Image optimization
        4. Thumbnail generation
        """
        if self.file and not self.pk:  # Only on creation
            try:
                self.file_size = self.file.size if hasattr(self.file, 'size') else 0
                self.file_extension = os.path.splitext(self.file.name)[1][1:].lower()

                # Process images
                if self.content_type == 'image':
                    try:
                        with Image.open(self.file) as img:
                            # Store original dimensions
                            self.width = img.width
                            self.height = img.height

                            # Validate image format
                            if img.format not in ALLOWED_IMAGE_FORMATS:
                                raise ValueError(f"Unsupported image format: {img.format}")

                            # Create WebP thumbnail
                            thumb_data = create_thumbnail(img)
                            if thumb_data:
                                thumbnail_name = f"{Path(self.file.name).stem}_thumb.webp"
                                self.thumbnail.save(
                                    thumbnail_name,
                                    ContentFile(thumb_data),
                                    save=False
                                )

                            # Optimize original image
                            optimized = optimize_image(img)
                            if optimized:
                                # Convert to WebP and save
                                optimized_io = BytesIO()
                                optimized.save(
                                    optimized_io, 
                                    format='WEBP', 
                                    quality=WEBP_QUALITY,
                                    method=6  # Highest compression method
                                )
                                
                                # Update filename to .webp
                                new_name = f"{Path(self.file.name).stem}.webp"
                                self.file.save(
                                    new_name,
                                    ContentFile(optimized_io.getvalue()),
                                    save=False
                                )
                                # Update file size after optimization
                                self.file_size = self.file.size
                                self.file_extension = 'webp'

                    except (IOError, OSError) as e:
                        logger.error(f"IO Error processing image {self.file.name}: {str(e)}")
                        raise
                    except ValueError as e:
                        logger.error(f"Validation error for image {self.file.name}: {str(e)}")
                        raise
                    except Exception as e:
                        logger.error(f"Unexpected error processing image {self.file.name}: {str(e)}")
                        raise

            except Exception as e:
                logger.error(f"Error in save method for file {self.file.name}: {str(e)}")
                raise

        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error saving file {self.file.name}: {str(e)}")
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
