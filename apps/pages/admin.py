from django.contrib import admin
from django.utils.html import format_html
from .models import Page, ContentBlock

class ContentBlockInline(admin.StackedInline):
    model = ContentBlock
    extra = 0
    fieldsets = (
        (None, {
            'fields': ('identifier', 'content_type', 'content', 'order')
        }),
    )

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
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
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'page', 'content_type', 'order', 'updated_at')
    list_filter = ('content_type', 'page')
    search_fields = ('identifier', 'page__title')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New instance
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
