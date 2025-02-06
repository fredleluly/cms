from django.contrib import admin
from django.utils.html import format_html
from .models import Page, ContentBlock, Article, ArticleCategory, MaintenanceMode
from unfold.admin import ModelAdmin, StackedInline

admin.site.site_header = 'Matana CMS'
admin.site.site_title = 'Matana CMS'
admin.site.index_title = 'Matana CMS'

class ContentBlockInline(StackedInline):
    model = ContentBlock
    extra = 0
    fieldsets = (
        (None, {
            'fields': ('identifier', 'content_type', 'content', 'order')
        }),
    )

@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'template', 'status', 'updated_at', 'view_page_link')
    list_filter = ('status', 'template', 'created_at')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentBlockInline]
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New instance
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # New instance
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

    def view_page_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">View Page</a>',
            f'/{obj.slug}/'
        )
    view_page_link.short_description = 'View'

@admin.register(ContentBlock)
class ContentBlockAdmin(ModelAdmin):
    list_display = ('identifier', 'page', 'content_type', 'order', 'updated_at')
    list_filter = ('content_type', 'page')
    search_fields = ('identifier', 'page__title')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New instance
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ArticleCategory)
class ArticleCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'published_at', 'created_by')
    list_filter = ('status', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'featured_image', 'excerpt', 'content')
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New instance
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(ModelAdmin):
    list_display = ('is_active', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('is_active', 'message'),
            'description': 'Enable or disable maintenance mode for the entire site.'
        }),
        ('Advanced Options', {
            'fields': ('allowed_ips',),
            'classes': ('collapse',),
            'description': 'Enter IP addresses that should have access during maintenance (comma-separated)'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        return not MaintenanceMode.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False
