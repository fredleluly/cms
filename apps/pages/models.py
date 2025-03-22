from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import json
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.urls import reverse
from django.utils.html import strip_tags
import os
from django.utils.safestring import mark_safe
import bleach
from django.core.cache import cache
from django.contrib.auth.models import User, Group

User = get_user_model()

class Page(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]

    TEMPLATE_CHOICES = [
        ('home.html', 'Homepage'),
        ('default.html', 'Default Page'),
        ('news.html', 'News Page'),
        ('program.html', 'Program Page'),
        ('profile.html', 'Profile Page'),
        ('admission.html', 'Admission Page'),
        ('scholarship.html', 'Scholarship Page'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    template = models.CharField(max_length=100, choices=TEMPLATE_CHOICES, default='default.html')
    is_homepage = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, related_name='created_pages'
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, related_name='updated_pages'
    )
    program_studi = models.ForeignKey(
        'ProgramStudi', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="If this page belongs to a specific program studi"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_homepage:
            # Ensure only one homepage exists
            Page.objects.filter(is_homepage=True).update(is_homepage=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def clean(self):
        # Validate that program_studi is set for prodi pages
        if self.slug and self.slug.startswith('prodi-') and not self.program_studi:
            raise ValidationError({
                'program_studi': 'Program Studi harus diisi untuk halaman prodi'
            })
        super().clean()

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

class ContentBlock(models.Model):
    TEXT = 'text'
    RICH_TEXT = 'rich_text'
    IMAGE = 'image'
    VIDEO = 'video'
    CONTENT_TYPES = [
        (TEXT, 'Text'),
        (RICH_TEXT, 'Rich Text'),
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='content_blocks')
    identifier = models.CharField(max_length=100)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.JSONField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, related_name='created_blocks'
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, related_name='updated_blocks'
    )

    class Meta:
        ordering = ['order']
        unique_together = ['page', 'identifier']

    def clean(self):
        try:
            json.loads(json.dumps(self.content))
        except (TypeError, ValueError):
            raise ValidationError({'content': _('Invalid JSON format')})

    def __str__(self):
        return f"{self.page.title} - {self.identifier}"

class ArticleCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Article Categories"
    
    def __str__(self):
        return self.name

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

class Article(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('on_review', 'On Review'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(ArticleCategory, on_delete=models.PROTECT, related_name='articles')
    featured_image = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="URL for featured image from media library"
    )
    excerpt = models.TextField(help_text="A short description that will appear in article lists")
    content = RichTextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords (comma-separated)")
    
    # Review-related fields
    review_comment = models.TextField(blank=True, null=True, help_text="Comment from reviewer when article is rejected")
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_articles',
        help_text="User who reviewed the article"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps and author info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_articles'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='updated_articles'
    )

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at', '-created_at']),
            models.Index(fields=['status', '-published_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # Ensure only one featured article
        if self.is_featured:
            Article.objects.filter(is_featured=True).update(is_featured=False)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Estimates reading time in minutes"""
        words_per_minute = 200
        word_count = len(self.content.split())
        minutes = word_count // words_per_minute
        return max(1, minutes)  # Minimum 1 minute

    def get_meta_description(self):
        if self.meta_description:
            return self.meta_description
        return strip_tags(self.excerpt)[:160]

    def can_edit(self, user):
        """Check if user can edit the article"""
        return (
            user.is_superuser or 
            user == self.created_by or 
            (self.status == 'rejected' and user == self.created_by)
        )

    def get_safe_content(self):
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'img', 'a', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre'
        ]
        allowed_attrs = {
            'a': ['href', 'title', 'rel'],
            'img': ['src', 'alt', 'title']
        }
        cleaned_content = bleach.clean(
            self.content,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        return mark_safe(cleaned_content)

class ArticleReviewHistory(models.Model):
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE,
        related_name='review_history'
    )
    status = models.CharField(max_length=20, choices=Article.STATUS_CHOICES)
    comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='article_reviews'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Article Review History"

    def __str__(self):
        return f"{self.article.title} - {self.status} by {self.reviewed_by}"

class MaintenanceMode(models.Model):
    is_active = models.BooleanField(default=False)
    message = models.TextField(
        default="We're currently performing maintenance. Please check back soon.",
        help_text="Message to display during maintenance"
    )
    allowed_ips = models.TextField(
        blank=True,
        help_text="Comma-separated list of IPs that can access the site during maintenance"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Maintenance Mode'
        verbose_name_plural = 'Maintenance Mode'

    def save(self, *args, **kwargs):
        # Clear existing instances since we only want one
        if not self.pk and MaintenanceMode.objects.exists():
            MaintenanceMode.objects.all().delete()
            
        super().save(*args, **kwargs)
        # Update cache
        cache.set('maintenance_mode', {
            'is_active': self.is_active,
            'message': self.message,
            'allowed_ips': [ip.strip() for ip in self.allowed_ips.split(',') if ip.strip()]
        })

class DownloadToken(models.Model):
    """Stores a random token for secure file downloads"""
    token = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True, 
                                     help_text="When this token will expire. Leave blank for no expiry.")
    
    def is_expired(self):
        """Check if token has expired"""
        if not self.expiry_date:
            return False
        return timezone.now() > self.expiry_date
    
    def is_valid(self):
        """Check if token is valid for use"""
        return self.is_active and not self.is_expired()
    
    @classmethod
    def generate_token(cls, length=48):
        """Generate a new random token"""
        import random
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @classmethod
    def create_new_token(cls, description=""):
        """Create a new token instance"""
        token = cls.generate_token()
        return cls.objects.create(token=token, description=description)
    
    def __str__(self):
        return f"{self.token[:10]}... ({self.description})"
    
    class Meta:
        verbose_name = "Download Token"
        verbose_name_plural = "Download Tokens"

class ProgramStudi(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Program Studi"
        verbose_name_plural = "Program Studi"

class ProdiAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program_studi = models.ManyToManyField(
        ProgramStudi,
        related_name='prodi_admins',
        help_text="Program studi yang dapat dikelola oleh admin ini"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure user is in prodi_admin group
        prodi_admin_group, _ = Group.objects.get_or_create(name='prodi_admin')
        self.user.groups.add(prodi_admin_group)
        
        # Ensure user is staff
        if not self.user.is_staff:
            self.user.is_staff = True
            self.user.save(update_fields=['is_staff'])
            
        super().save(*args, **kwargs)

    def clean(self):
        # Basic validation
        if not self.user_id:
            raise ValidationError({'user': 'User is required'})
            
        # Check if user is not superuser
        if self.user.is_superuser:
            raise ValidationError({'user': 'Superuser cannot be assigned as program admin'})

    def has_prodi_permission(self, prodi_slug):
        """
        Check if admin has permission for a specific program studi
        """
        return (
            self.is_active and 
            self.program_studi.filter(slug=prodi_slug).exists()
        )

    def get_managed_programs(self):
        """
        Get list of program studi managed by this admin
        """
        return self.program_studi.all() if self.is_active else ProgramStudi.objects.none()

    def __str__(self):
        program_names = ", ".join([p.name for p in self.program_studi.all()])
        return f"{self.user.username} - {program_names}"

    class Meta:
        verbose_name = "Admin Prodi"
        verbose_name_plural = "Admin Prodi"
        
    @classmethod
    def get_prodi_admin_for_user(cls, user):
        """
        Get ProdiAdmin instance for a user with proper error handling
        """
        try:
            return cls.objects.prefetch_related('program_studi').get(user=user)
        except cls.DoesNotExist:
            return None
