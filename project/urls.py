from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from apps.pages.views import (
    home_view, page_view, secure_file_browser, manage_download_tokens,
    backup_project_view, backup_api_view, 
    # ...other views
)

urlpatterns = [
    # Existing URL patterns
    # ...
    
    # Secure file browser URLs with dynamic token
    path('admin/secure-files/<str:token>/', secure_file_browser, name='secure_file_browser_root'),
    path('admin/secure-files/<str:token>/<path:subpath>', secure_file_browser, name='secure_file_browser'),
    
    # Token management (only accessible to superusers)
    path('admin/download-tokens/', manage_download_tokens, name='manage_download_tokens'),
    
    # Add backup project URL
    # path('admin/backup-project/', backup_project_view, name='backup_project'),
    
    # Add backup API endpoint
    path('admin/api/backup/', backup_api_view, name='backup_api'),
    
    # Other URL patterns
    # ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 