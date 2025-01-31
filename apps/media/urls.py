from django.urls import path
from . import views

app_name = 'media'

urlpatterns = [
    path('library/', views.media_library, name='library'),
    path('upload/', views.upload_media, name='upload_media'),
    path('delete/<int:id>/', views.delete_media, name='delete_media'),
] 