from django.contrib import admin
from django.utils.html import format_html
from .models import MediaFile

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'content_type', 'formatted_file_size', 
                   'uploaded_by', 'uploaded_at', 'is_public')
    list_filter = ('content_type', 'is_public', 'uploaded_at')
    search_fields = ('title', 'description', 'tags')
    readonly_fields = ('file_size', 'width', 'height', 'thumbnail_preview', 
                      'uploaded_at', 'file_extension')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'file', 'content_type', 'tags')
        }),
        ('File Information', {
            'fields': ('file_size', 'file_extension', 'width', 'height', 'thumbnail_preview')
        }),
        ('Settings', {
            'fields': ('is_public', 'uploaded_by')
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />', 
                obj.thumbnail.url
            )
        return format_html(
            '<i class="fas {} fa-2x"></i>', 
            obj.file_type_icon
        )
    thumbnail_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set uploaded_by on creation
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
