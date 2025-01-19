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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_homepage:
            # Ensure only one homepage exists
            Page.objects.filter(is_homepage=True).update(is_homepage=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

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
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(ArticleCategory, on_delete=models.PROTECT, related_name='articles')
    featured_image = models.ImageField(
        upload_to='articles/',
        validators=[validate_file_extension]
    )
    excerpt = models.TextField(help_text="A short description that will appear in article lists")
    content = RichTextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords (comma-separated)")
    
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

    def clean(self):
        if self.featured_image and self.featured_image.size > 5*1024*1024:  # 5MB
            raise ValidationError('File too large')

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
