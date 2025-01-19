from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from .models import Page, Article, ArticleCategory
from django.contrib.admin.views.decorators import staff_member_required

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

def news_view(request):
    # Get query parameters with defaults
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('search', '').strip()
    page_number = request.GET.get('page', 1)
    
    # Base queryset with select_related for performance
    articles = Article.objects.select_related('category', 'created_by').filter(status='published')
    
    # Apply filters
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Featured article - only show if no search/filter is active
    featured_article = None
    if not (category_slug or search_query):
        featured_article = articles.filter(is_featured=True).first()
        if featured_article:
            articles = articles.exclude(id=featured_article.id)
    
    # Get total count before pagination
    total_count = articles.count()
    
    # Pagination
    paginator = Paginator(articles, 9)  # 9 articles per page
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Get all categories with article counts
    categories = ArticleCategory.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    )
    
    context = {
        'featured_article': featured_article,
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'total_articles': total_count,
    }
    
    return render(request, 'pages/news.html', context)

def article_detail_view(request, slug):
    article = get_object_or_404(
        Article.objects.select_related('category', 'created_by'),
        slug=slug,
        status='published'
    )
    
    # Get related articles
    related_articles = Article.objects.select_related('category').filter(
        category=article.category,
        status='published'
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    
    return render(request, 'pages/article_detail.html', context)

@staff_member_required
def dashboard_view(request):
    # Get query parameters
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)
    
    # Base queryset
    articles = Article.objects.select_related('category', 'created_by')
    
    # Apply filters
    if category_id:
        articles = articles.filter(category_id=category_id)
    if status:
        articles = articles.filter(status=status)
    if search:
        articles = articles.filter(
            Q(title__icontains=search) |
            Q(excerpt__icontains=search)
        )
    
    # Get counts for stats
    total_articles = Article.objects.count()
    published_count = Article.objects.filter(status='published').count()
    draft_count = Article.objects.filter(status='draft').count()
    
    # Get categories with counts
    categories = ArticleCategory.objects.annotate(
        article_count=Count('articles')
    )
    
    # Pagination
    paginator = Paginator(articles, 20)
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles_page,
        'categories': categories,
        'total_articles': total_articles,
        'published_count': published_count,
        'draft_count': draft_count,
        'selected_category': category_id,
        'selected_status': status,
        'search_query': search,
    }
    
    return render(request, 'admin/dashboard.html', context)
