from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import MediaFile
from django.core.paginator import Paginator
import os
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Q
from apps.pages.models import ProdiAdmin
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.

@login_required
def media_library(request):

    # Check if user has media program studi permission
    if not request.user.is_superuser:
        try:
            prodi_admin = ProdiAdmin.objects.get(user=request.user)
            is_media_admin = prodi_admin.program_studi.filter(slug='media').exists()
            if not is_media_admin:
                messages.error(request, 'Anda tidak memiliki izin untuk mengedit media.')
                return redirect('content_dashboard')
        except ProdiAdmin.DoesNotExist:
            messages.error(request, 'Anda tidak memiliki izin untuk mengedit media.')
            return redirect('content_dashboard')

    select_mode = request.GET.get('mode') == 'select'
    print(f"Select mode: {select_mode}")  # Debug log
    media_files = MediaFile.objects.all().order_by('-uploaded_at')
    
    # Get counts for different file types
    context = {
        'image_count': MediaFile.objects.filter(content_type='image').count(),
        'document_count': MediaFile.objects.filter(content_type='document').count(),
        'video_count': MediaFile.objects.filter(content_type='video').count(),
        'audio_count': MediaFile.objects.filter(content_type='audio').count(),
    }
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        media_files = media_files.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Handle filtering
    media_type = request.GET.get('type', '')
    if media_type and media_type != 'all':
        media_files = media_files.filter(content_type=media_type)
    
    # Pagination with preserved query parameters
    paginator = Paginator(media_files, 24)
    page = request.GET.get('page')
    media_files = paginator.get_page(page)
    
    context.update({
        'media_files': media_files,
        'select_mode': select_mode,
        'search_query': search_query,
        'current_type': media_type,
    })
    
    return render(request, 'media/library.html', context)

@login_required
@require_POST
def upload_media(request):
    try:
        files = request.FILES.getlist('files[]')
        if not files:
            return JsonResponse({
                'status': 'error',
                'message': 'No files were uploaded'
            }, status=400)

        # Validate file sizes
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        for file in files:
            if file.size > MAX_FILE_SIZE:
                return JsonResponse({
                    'status': 'error',
                    'message': f'File {file.name} is too large. Maximum size is 10MB.'
                }, status=400)

        uploaded_files = []
        
        for file in files:
            try:
                content_type = determine_content_type(file.name)
                
                media = MediaFile(
                    title=file.name,
                    file=file,
                    uploaded_by=request.user,
                    content_type=content_type
                )
                
                # Generate thumbnail for images
                if content_type == 'image':
                    try:
                        img = Image.open(file)
                        img.thumbnail((300, 300))
                        thumb_io = BytesIO()
                        img.save(thumb_io, format='JPEG')
                        
                        thumbnail_name = f'thumb_{file.name}'
                        media.thumbnail.save(
                            thumbnail_name,
                            ContentFile(thumb_io.getvalue()),
                            save=False
                        )
                    except Exception as e:
                        print(f"Thumbnail generation error: {str(e)}")
                
                media.save()
                
                uploaded_files.append({
                    'id': media.id,
                    'title': media.title,
                    'url': media.file.url,
                    'thumbnail': media.thumbnail.url if media.thumbnail else None,
                })
            except Exception as e:
                print(f"Error uploading file {file.name}: {str(e)}")
                continue

        return JsonResponse({
            'status': 'success',
            'files': uploaded_files
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_POST
@login_required
def delete_media(request, id):
    try:
        media = MediaFile.objects.get(id=id)
        # Delete file from storage
        if media.file:
            media.file.delete()
        # Delete database record
        media.delete()
        return JsonResponse({'status': 'success'})
    except MediaFile.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Media not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def determine_content_type(filename):
    ext = filename.lower().split('.')[-1]
    
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    document_extensions = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx'}
    video_extensions = {'mp4', 'avi', 'mov', 'wmv'}
    audio_extensions = {'mp3', 'wav', 'ogg', 'm4a'}
    
    if ext in image_extensions:
        return 'image'
    elif ext in document_extensions:
        return 'document'
    elif ext in video_extensions:
        return 'video'
    elif ext in audio_extensions:
        return 'audio'
    else:
        return 'other'
