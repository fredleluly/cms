from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import json

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
