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
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Create a registry to track views decorated with togglable_cache
CACHED_VIEWS_REGISTRY = {}

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

def togglable_cache(timeout=None, *, key_prefix=None, cache=None, description=None):
    """
    A decorator that implements Django's cache_page with the ability to toggle it on/off.
    
    Args:
        timeout: Cache timeout in seconds. If None, uses settings.CACHE_TIMEOUT.
        key_prefix: A prefix for the cache key to help distinguish cache entries.
        cache: The cache backend to use. If None, uses the default cache.
        description: Human-readable description of what this view displays (for admin UI)
    
    Usage:
        @togglable_cache(60*60, description="Homepage")
        def my_view(request):
            # View logic here
            return render(request, 'template.html', context)
    
    To disable caching for all views:
        1. Set CACHE_ENABLED=False in settings or .env
    
    To clear the cache for a specific view:
        from django.core.cache import cache
        cache.delete_pattern(f"views.decorators.cache.cache_page.{key_prefix}.*")
    """
    if timeout is None:
        timeout = getattr(settings, 'CACHE_TIMEOUT', 3600 * 48)  # Default to 1 hour
    
    def decorator(view_func):
        view_name = view_func.__name__
        
        # Register this view in our registry
        CACHED_VIEWS_REGISTRY[view_name] = {
            'name': view_name,
            'description': description or view_name.replace('_', ' ').title(),
            'timeout': timeout,
            'key_prefix': key_prefix
        }
        
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            try:
                # Check if caching is enabled globally
                cache_enabled = getattr(settings, 'CACHE_ENABLED', True)
                
                # Check for cache override in request query params (for superusers/staff only)
                if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
                    cache_override = request.GET.get('cache', None)
                    if cache_override is not None:
                        # Allow staff/superusers to override cache setting via URL param
                        cache_enabled = cache_override.lower() in ('true', '1', 'yes')
                
                if cache_enabled:
                    # Apply cache_page decorator dynamically
                    cached_view = cache_page(timeout, key_prefix=key_prefix, cache=cache)(view_func)
                    return cached_view(request, *args, **kwargs)
                else:
                    # Skip caching
                    return view_func(request, *args, **kwargs)
            except Exception as e:
                # Log the error and fall back to uncached view
                logger.error(f"Cache error in {view_func.__name__}: {str(e)}")
                return view_func(request, *args, **kwargs)
        
        return wrapped_view
    
    return decorator

def clear_view_cache(view_name=None, key_prefix=None):
    """
    Utility function to clear the cache for a specific view or all views.
    
    Args:
        view_name: The name of the view to clear. If None, clears all views with the given key_prefix.
        key_prefix: The key prefix used by the cache. If None, uses the default.
    
    Returns:
        bool: True if cache was successfully cleared, False otherwise.
    """
    try:
        if key_prefix is None:
            key_prefix = 'views.decorators.cache.cache_page'
        
        pattern = f"{key_prefix}.*"
        if view_name:
            # Check if view has a custom key_prefix in the registry
            if view_name in CACHED_VIEWS_REGISTRY and CACHED_VIEWS_REGISTRY[view_name].get('key_prefix'):
                pattern = f"{CACHED_VIEWS_REGISTRY[view_name]['key_prefix']}.*"
            else:
                pattern = f"{key_prefix}.{view_name}.*"
            
        # Django's default cache doesn't have delete_pattern method
        # so we'll need to handle this differently based on the cache backend
        if hasattr(cache, 'delete_pattern'):
            # Redis and some other backends have delete_pattern
            cache.delete_pattern(pattern)
        else:
            # For default cache, we can only clear the entire cache
            cache.clear()
            
        logger.info(f"Cache cleared for pattern: {pattern}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        return False 