from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.cache import cache
from .models import Page

# Create your views here.

def home_view(request):
    try:
        page = Page.objects.get(is_homepage=True, status=Page.PUBLISHED)
    except Page.DoesNotExist:
        page = Page.objects.filter(status=Page.PUBLISHED).first()
        if not page:
            raise Http404("No homepage found")
    
    # Get cached content or generate new
    cache_key = f'page_content_{page.id}'
    content_blocks = cache.get(cache_key)
    
    if content_blocks is None:
        content_blocks = {}
        for block in page.content_blocks.all():
            content_blocks[block.identifier] = {
                'type': block.content_type,
                'content': block.content
            }
        cache.set(cache_key, content_blocks, timeout=300)  # Cache for 5 minutes
    
    context = {
        'page': page,
        'content': content_blocks,
        'meta': page.metadata
    }
    
    return render(request, f'pages/{page.template}', context)

def page_view(request, slug):
    page = get_object_or_404(Page, slug=slug, status=Page.PUBLISHED)
    
    # Convert content blocks to a dictionary for easy access in templates
    content_blocks = {}
    for block in page.content_blocks.all():
        content_blocks[block.identifier] = {
            'type': block.content_type,
            'content': block.content
        }
    
    template_name = f"pages/{page.template}.html"
    
    context = {
        'page': page,
        'content': content_blocks,
        'meta': page.metadata
    }
    
    return render(request, template_name, context)
