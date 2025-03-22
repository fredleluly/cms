from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps
import logging
import os
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

def superuser_required(view_func):
    """
    Decorator for views that checks if the user is a superuser.
    If not, returns a 403 Forbidden response.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning(f"Unauthenticated user tried to access protected view: {request.path}")
            return redirect(f"{reverse('admin:login')}?next={request.path}")
        
        if not request.user.is_superuser:
            logger.warning(f"Non-superuser user {request.user.username} tried to access superuser-only view: {request.path}")
            return HttpResponseForbidden("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def safe_join_paths(base, *paths):
    """
    Safely join base path with user-provided paths, preventing path traversal attacks.
    Returns None if the resulting path would escape the base directory.
    """
    try:
        base_path = Path(base).resolve()
        joined_path = base_path.joinpath(*paths).resolve()
        
        # Check if the joined path is still within the base path
        if base_path in joined_path.parents or joined_path == base_path:
            return joined_path
        else:
            logger.warning(f"Attempted path traversal: {paths} from base {base}")
            return None
    except (ValueError, TypeError) as e:
        logger.error(f"Error joining paths: {e}")
        return None

def get_file_details(path):
    """Get file details for directory listing"""
    try:
        stat_info = os.stat(path)
        is_dir = os.path.isdir(path)
        size = stat_info.st_size if not is_dir else 0
        modified = stat_info.st_mtime
        
        return {
            'name': os.path.basename(path),
            'path': path,
            'is_dir': is_dir,
            'size': size,
            'modified': modified,
            'content_type': 'directory' if is_dir else mimetypes.guess_type(path)[0] or 'application/octet-stream'
        }
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"Error getting file details for {path}: {e}")
        return None 