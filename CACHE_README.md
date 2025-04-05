# Togglable Page Caching in Django

This document explains how to use the togglable page caching system implemented in this project.

## Overview

The togglable caching system allows you to:

1. Cache specific views for better performance (default cache time: 1 hour)
2. Easily toggle caching on and off globally via settings or environment variables
3. Override cache settings for specific views when needed (for staff/superusers)
4. Clear cache for specific views or all views via an admin interface

## Admin Interface

A new admin page has been created to manage caching settings:

- **URL**: `/admin/cache-management/`
- **Access**: Only staff members can access this page
- **Features**:
  - Enable/disable global caching
  - Clear cache for specific views or all views
  - View current cache settings and status

## Usage for Developers

### Applying Cache to a View

To apply togglable caching to a view, use the `togglable_cache` decorator:

```python
from apps.pages.utils import togglable_cache

@togglable_cache(timeout=60*60, key_prefix='my_view')
def my_view(request):
    # View logic here
    return render(request, 'template.html', context)
```

### Parameters

- `timeout`: Cache timeout in seconds (defaults to `settings.CACHE_TIMEOUT` which is 3600 seconds/1 hour)
- `key_prefix`: A prefix for the cache key to help identify this view's cache entries
- `cache`: The cache backend to use (defaults to the default cache)

### Toggling Cache On/Off

#### 1. Global Toggle

Edit your `.env` file to toggle caching globally:

```
CACHE_ENABLED=True  # Enable caching
# or
CACHE_ENABLED=False  # Disable caching
```

You can also modify the `CACHE_ENABLED` setting in the admin interface.

#### 2. Per-Request Toggle (for staff/superusers)

Staff and superusers can temporarily disable caching for a specific view by adding `?cache=false` to any URL:

```
http://example.com/some-page/?cache=false
```

This is useful when making changes and needing to see them immediately without clearing the entire cache.

### Clearing the Cache

#### From the Admin Interface

1. Go to `/admin/cache-management/`
2. Select the view you want to clear from the dropdown
3. Click "Clear Cache"

#### Programmatically

```python
from apps.pages.utils import clear_view_cache

# Clear cache for a specific view
clear_view_cache(view_name='home_view')

# Clear all caches
clear_view_cache()
```

## Currently Cached Views

The following views have been configured with togglable caching:

1. `home_view` - The website homepage
2. `news_view` - The news listing page
3. `article_detail_view` - Individual article pages

## Best Practices

1. **Use caching for read-heavy pages**: Apply caching to pages that are frequently read but infrequently updated.
2. **Be careful with user-specific content**: Avoid caching pages with user-specific content or use a different caching strategy for those.
3. **Consider appropriate cache timeouts**: Adjust the timeout based on how frequently the content changes.
4. **Clear cache when updating important content**: Use the admin interface to clear relevant caches after making significant content updates.

## Troubleshooting

If you see stale content even after disabling caching:

1. Make sure you're logged in as a staff/superuser when using the `?cache=false` parameter
2. Try clearing the specific view's cache from the admin interface
3. Check if any intermediate caching (e.g., CDN, browser cache) might be causing the issue
4. If all else fails, restart the Django server to clear all in-memory cache

## Error Handling

The caching system includes error handling to ensure that if any caching operation fails, the system will fall back to serving uncached content rather than showing an error. 