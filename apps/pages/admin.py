from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import Page, ContentBlock, Article, ArticleCategory, MaintenanceMode, ProgramStudi, ProdiAdmin
from unfold.admin import ModelAdmin, StackedInline
from django.db import transaction
# from django.contrib.admin import ModelAdmin, StackedInline


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
    list_display = ('title', 'slug', 'program_studi', 'status', 'updated_at', 'view_page_link')
    list_filter = ('status', 'program_studi')
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='prodi_admin').exists():
            try:
                prodi_admin = ProdiAdmin.objects.get(user=request.user)
                return qs.filter(program_studi=prodi_admin.program_studi)
            except ProdiAdmin.DoesNotExist:
                return qs.none()
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        if request.user.groups.filter(name='prodi_admin').exists():
            try:
                prodi_admin = ProdiAdmin.objects.get(user=request.user)
                return obj.program_studi == prodi_admin.program_studi
            except ProdiAdmin.DoesNotExist:
                return False
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "program_studi" and not request.user.is_superuser:
            if request.user.groups.filter(name='prodi_admin').exists():
                try:
                    prodi_admin = ProdiAdmin.objects.get(user=request.user)
                    kwargs["queryset"] = ProgramStudi.objects.filter(id=prodi_admin.program_studi.id)
                except ProdiAdmin.DoesNotExist:
                    kwargs["queryset"] = ProgramStudi.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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

@admin.register(ProgramStudi)
class ProgramStudiAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProdiAdmin)
class ProdiAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_program_studi', 'is_active', 'created_at')
    list_filter = ('program_studi', 'is_active')
    search_fields = ('user__username', 'program_studi__name')
    
    def get_program_studi(self, obj):
        return ", ".join([p.name for p in obj.program_studi.all()])
    get_program_studi.short_description = 'Program Studi'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Ensure user is staff
        obj.user.is_staff = True
        obj.user.save()
        
        # Add user to prodi_admin group
        prodi_admin_group = Group.objects.get(name='prodi_admin')
        obj.user.groups.add(prodi_admin_group)
        
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

