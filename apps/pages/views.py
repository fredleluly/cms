from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from .models import Page, Article, ArticleCategory, ContentBlock
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from functools import wraps
import time
from django.utils.text import slugify
from django import forms
from ckeditor.widgets import CKEditorWidget
import uuid
import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import json
from apps.media.models import MediaFile
from django.urls import reverse
import logging

# Get logger for this file
logger = logging.getLogger(__name__)

def custom_404(request, exception):

    return render(request, '404.html', status=404)



# Create your views here.

def create_standardized_blocks(page, blocks_data):
    """Helper function to create standardized content blocks"""
    for block in blocks_data:
        ContentBlock.objects.create(
            page=page,
            identifier=block['identifier'],
            content_type=ContentBlock.RICH_TEXT,  # Using RICH_TEXT as standard
            content={
                'title': block.get('title', ''),
                'subtitle': block.get('subtitle', ''),
                'description': block.get('description', ''),
                'image': block.get('image', ''),
                'items': block.get('items', []),
                'background_image': block.get('background_image', ''),
                'cta': block.get('cta', {
                    'text': '',
                    'url': '',
                    'style': 'primary'
                }),
                'layout': block.get('layout', 'default'),
                'settings': block.get('settings', {})
            },
            order=block['order']
        )

def create_default_homepage():
    """Create a default homepage if none exists"""
    homepage = Page.objects.create(
        title="Welcome to Matana University",
        slug="home",
        is_homepage=True,
        status=Page.PUBLISHED,
        template='home.html'
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Welcome to Matana University',
            'subtitle': 'Perguruan tinggi terpercaya dan terkemuka dalam akademik dan profesionalisme',
            'background_image': '/static/images/hero-bg.jpg',
            'cta': {
                'text': 'Learn More',
                'url': '/about',
                'style': 'primary'
            },
            'order': 1
        },
        {
            'identifier': 'section1',
            'title': 'banner section',
            'subtitle': '',
            'items': [
                {
                    'title': 'banner1',
                    'image': '/static/images/banner.jpg',
                },
                {
                    'title': 'banner2',
                    'image': '/static/images/banner2.jpg',
                },
                {
                    'title': 'banner3',
                    'image': '/static/images/banner3.jpg',
                },
                {
                    'title': 'banner4',
                    'image': '/static/images/banner4.jpg',
                },
            ],
         
            'order': 1
        },
        {
            'identifier': 'section2',
            'title': '',
            'items': [
                {
                    'title': 'Menerapkan kurikulum akademik yang mendukung lulusan siap berkompetisi di dunia kerja.',
                },
                {
                    'title': 'Dosen yang profesional, praktisi, dan berprestasi di dalam dan luar negeri.',
                },
                {
                    'title': 'Memiliki fasilitas yang mendukung praktik dari teori pembelajaran setiap program.',
                },
                {
                    'title': 'Kesempatan magang dan berkarir di Paramount Group & Mitra Bisnis lainnya, serta menjadi Entrepreneur',
                },
                {
                    'title': 'Memiliki program Student Exchange (pertukaran mahasiswa) ke universitas ternama di Asia dan Eropa.',
                },
            ],
            'order': 2
        },
        {
            'identifier': 'section3',
            'title': 'Penerimaan Mahasiswa Baru',
            'background_image': '/static/images/section3.jpg',
            'items': [
                {
                    'title': '',
                    'description': 'Tahun Akademik 2025/2026',
                },
                {
                    'title': '',
                    'description': 'Matana University menyelenggarakan berbagai lokakarya berbasis dunia usaha, program magang di berbagai industri, ruang inkubator di kampus, dan kompetisi rencana bisnis tahunan dengan penghargaan untuk mahasiswa wirausaha yang terbaik.',
                },
                {
                    'title': '',
                    'description': 'https://matanauniversity.siakadcloud.com/spmbfront/',
                }
            ],
            'order': 3
        },
        {
            'identifier': 'section4',
            'title': 'Berita Dan Acara',
            'subtitle': 'Stay updated with the latest news and events from Matana University',
            # 'description': 'https://www.youtube.com/embed/u2lqeWCrtL0?si=NVxrT45j0kzH0mk0',
            'description': 'https://www.youtube.com/embed/AMLKY6NBjz0',
            'order': 4
        },
        {
            'identifier': 'section5',
            'title': 'Virtual Tour 360 Matana University',
             'background_image': '/static/images/section5.jpg',
            'description': 'http://360.matanauniversity.ac.id/',
            'order': 5
        },
        {
            'identifier': 'section6',
            'title': 'Follow Instagram Kami',
            'description': 'https://www.instagram.com/matanauniversityofficial/',
            'items': [
                {
                    'title': 'https://www.instagram.com/p/DFchJtQsUua/',
                    'image': '/static/images/instagram1.jpg',
                },
                {
                    'title': 'https://www.instagram.com/p/DFZOdJ9yFTc/',
                    'image': '/static/images/instagram2.jpg',
                },
                {
                    'title': 'https://www.instagram.com/p/DFT1BvYSDB2/',
                    'image': '/static/images/instagram3.jpg',
                },
                {
                    'title': 'https://www.instagram.com/p/DFO5HGrPN-S/',
                    'image': '/static/images/instagram4.jpg',
                }
            ],
            'order': 6
        }

    ]
    
    create_standardized_blocks(homepage, default_blocks)
    return homepage

def home_view(request):
    try:
        page = Page.objects.get(is_homepage=True, status=Page.PUBLISHED)
    except Page.DoesNotExist:
        try:
            page = Page.objects.filter(status=Page.PUBLISHED).first()
            if page:
                page.is_homepage = True
                page.save()
            else:
                page = create_default_homepage()
        except Exception as e:
            raise Http404(f"Could not create homepage: {str(e)}")
    
    # Get cached content or generate new
    # cache_key = f'page_content_{page.id}'
    # blocks = cache.get(cache_key)
    
    # if blocks is None:
    #     blocks = {}
    #     for block in page.content_blocks.all().order_by('order'):
    #         blocks[block.identifier] = {
    #             'type': block.content_type,
    #             'content': block.content
    #         }
    #     cache.set(cache_key, blocks, timeout=300)  # Cache for 5 minutes
    
    blocks = {}
    for block in page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # tambahakn 4 berita terbaru
    berita_terbaru = Article.objects.filter(status='published').order_by('-created_at')[:4]
    blocks['berita_terbaru'] = berita_terbaru

    context = {
        'page': page,
        'meta': page.metadata,
        'blocks': blocks  # Simplified - just send all blocks
    }
    
    return render(request, f'pages/{page.template}', context)

def page_view(request, slug):
    page = get_object_or_404(Page, slug=slug, status=Page.PUBLISHED)
    
    try:
        # Get content blocks with error handling
        blocks = {}
        for block in page.content_blocks.all().order_by('order'):
            try:
                blocks[block.identifier] = block.content
            except Exception as e:
                # Log error but continue processing other blocks
                print(f"Error processing block {block.identifier}: {str(e)}")
                continue
        
        context = {
            'page': page,
            'meta': page.metadata,
            'blocks': blocks  # Simplified - just send all blocks
        }
        
        template_name = f"pages/{page.template}.html"
        return render(request, template_name, context)
        
    except Exception as e:
        # Log the error and return a 500 error
        print(f"Error rendering page {slug}: {str(e)}")
        raise Http404("Page could not be rendered")

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

    # print(article.content)
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    
    return render(request, 'pages/article_detail.html', context)

@staff_member_required
def dashboard_view(request):
    """Dashboard view"""
    context = {
        'total_articles': Article.objects.count(),
        'published_count': Article.objects.filter(status='published').count(),
        'draft_count': Article.objects.filter(status='draft').count(),
        'articles': Article.objects.all().order_by('-created_at')[:5],
        'pages': Page.objects.all(),
        'latest_page_update': Page.objects.order_by('-updated_at').first().updated_at if Page.objects.exists() else None,
        'categories': ArticleCategory.objects.annotate(article_count=Count('articles')),
        'most_used_category': ArticleCategory.objects.annotate(
            article_count=Count('articles')
        ).order_by('-article_count').first(),
        'media_count': MediaFile.objects.count(),
        'storage_used': '2.1 GB',  # You should calculate this
        'storage_limit': '5 GB',  # Your storage limit
    }
    return render(request, 'admin/dashboard.html', context)

class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Article
        fields = ['title', 'excerpt', 'content', 'category', 'featured_image', 
                 'meta_description', 'meta_keywords', 'is_featured']

@staff_member_required
def article_create_view(request):
    form = ArticleForm()
    categories = ArticleCategory.objects.all()
    context = {
        'form': form,
        'categories': categories,
        'action': 'create',
        'title': 'Create New Article'
    }
    return render(request, 'admin/article_form.html', context)

@staff_member_required
def article_edit_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    form = ArticleForm(instance=article)
    categories = ArticleCategory.objects.all()
    context = {
        'form': form,
        'article': article,
        'categories': categories,
        'action': 'edit',
        'title': f'Edit Article: {article.title}'
    }
    return render(request, 'admin/article_form.html', context)

@staff_member_required
@require_POST
def article_save_view(request):
    # Handle quick category creation
    if request.POST.get('action') == 'create_category':
        name = request.POST.get('new_category')
        slug = request.POST.get('category_slug') or slugify(name)
        
        category = ArticleCategory.objects.create(
            name=name,
            slug=slug,
        )
        messages.success(request, f'Category "{name}" created successfully.')
        return redirect(request.path)

    article_id = request.POST.get('article_id')
    
    if article_id:
        article = get_object_or_404(Article, id=article_id)
    else:
        article = Article(created_by=request.user)
    
    # # Handle image upload
    # if 'featured_image' in request.FILES:
    #     if article.featured_image:
    #         default_storage.delete(article.featured_image.path)
    #     article.featured_image = request.FILES['featured_image']
    
    # Update fields
    print(f"Request from save view #######: {request.POST}")

    article.featured_image = request.POST.get('featured_image')
    article.title = request.POST.get('title')
    article.slug = request.POST.get('slug') or slugify(article.title)
    article.category_id = request.POST.get('category')
    article.excerpt = request.POST.get('excerpt')
    article.content = request.POST.get('content')
    article.status = request.POST.get('status')
    article.meta_description = request.POST.get('meta_description')
    article.meta_keywords = request.POST.get('meta_keywords')
    article.is_featured = request.POST.get('is_featured') == 'on'
    
    if article.status == 'published' and not article.published_at:
        article.published_at = timezone.now()
    
    article.updated_by = request.user
    article.save()
    
    messages.success(request, f'Article "{article.title}" has been saved successfully.')
    return redirect('content_dashboard')

@staff_member_required
@require_POST
def article_delete_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    title = article.title
    
    article.delete()
    messages.success(request, f'Article "{title}" has been deleted successfully.')
    return JsonResponse({'status': 'success'})

@staff_member_required
@require_POST
def article_quick_update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    field = request.POST.get('field')
    value = request.POST.get('value')
    
    if field == 'status':
        article.status = value
        if value == 'published' and not article.published_at:
            article.published_at = timezone.now()
    elif field == 'is_featured':
        article.is_featured = value == 'true'
    
    article.updated_by = request.user
    article.save()
    
    return JsonResponse({
        'status': 'success',
        'published_at': article.published_at.strftime('%b %d, %Y') if article.published_at else '-'
    })

def create_default_profile_page():
    """Create default profile page with standardized content blocks"""
    profile_page = Page.objects.create(
        title="Profil Matana University",
        slug="profil-matana",
        template='profile.html',
        status=Page.PUBLISHED,
        metadata={
            'meta_description': 'Profil Matana University - Perguruan tinggi terpercaya dan terkemuka',
            'meta_keywords': 'profil matana, visi misi matana, sejarah matana'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Profil Matana University',
            'subtitle': 'World Class Learning Experience',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1
        },
        {
            'identifier': 'visi_section',
            'title': 'Visi Matana',
            'description': 'Menjadi Perguruan Tinggi terpercaya dan terkemuka dalam akademik dan profesionalisme yang berwawasan nasional dan internasional...',
            'order': 2
        },
        {
            'identifier': 'misi_section',
            'title': 'Misi Matana',
            'items': [
                {
                    'title': 'Kepemimpinan',
                    'description': 'Terbentuknya lulusan yang memiliki jiwa kepemimpinan...'
                },
                {
                    'title': 'Penelitian',
                    'description': 'Terciptanya lulusan yang memiliki kemampuan penelitian...'
                },
                {
                    'title': 'Kepedulian Sosial',
                    'description': 'Terbentuknya generasi penerus yang memiliki kepedulian...'
                }
            ],
            'order': 3
        },
        {
            'identifier': 'sejarah_section',
            'title': 'Sejarah Matana',
            'description': 'Universitas Matana mulai beroperasi pada bulan Agustus 2014...',
            'image': '/static/images/history.jpg',
            'order': 4
        },
        {
            'identifier': 'keunggulan_section',
            'title': 'Keunggulan Matana',
            'items': [
                {
                    'title': 'Kurikulum Akademik Unggul',
                    'description': 'Menerapkan kurikulum akademik yang mendukung...',
                    'image': '/media/keunggulan/academic.jpg'
                }
            ],
            'order': 5
        }
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

def profile_view(request):
    """View for profile page"""
    try:
        profile_page = Page.objects.get(
            slug='profil-matana',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks  # Simplified - just send all blocks
    }
    
    return render(request, 'pages/profile.html', context)

def ratelimit(key='ip', rate='5/m'):
    def decorator(func):
        @wraps(func)
        def wrapped(request, *args, **kwargs):
            if request.user.is_staff:  # Skip untuk admin
                return func(request, *args, **kwargs)
                
            # Get identifier (IP address atau user ID)
            if key == 'ip':
                ident = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            else:
                ident = request.user.id
                
            # Parse rate limit
            count, period = rate.split('/')
            count = int(count)
            multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
            period = int(period[:-1]) * multiplier[period[-1]]
            
            # Check cache
            cache_key = f'ratelimit_{func.__name__}_{ident}'
            requests = cache.get(cache_key, [])
            now = time.time()
            
            # Clean old requests
            requests = [req for req in requests if now - req < period]
            
            if len(requests) >= count:
                raise PermissionDenied('Rate limit exceeded')
                
            requests.append(now)
            cache.set(cache_key, requests, period)
            
            return func(request, *args, **kwargs)
        return wrapped
    return decorator

@ratelimit(rate='3/m')
def contact_form_view(request):
    # View logic here
    pass

@staff_member_required
@require_POST
def category_create_view(request):
    name = request.POST.get('new_category')
    if not name:
        messages.error(request, 'Category name is required')
        return JsonResponse({'error': 'Category name is required'}, status=400)
        
    slug = request.POST.get('category_slug') or slugify(name)
    
    try:
        category = ArticleCategory.objects.create(
            name=name,
            slug=slug,
            # created_by=request.user
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug
                }
            })
            
        messages.success(request, f'Category "{name}" created successfully.')
        return redirect(request.META.get('HTTP_REFERER', 'content_dashboard'))
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
            
        messages.error(request, f'Error creating category: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'content_dashboard'))

@staff_member_required
@require_POST
def upload_image(request):
    if 'image' in request.FILES:
        image = request.FILES['image']
        # Generate unique filename
        filename = f"article_images/{timezone.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}{os.path.splitext(image.name)[1]}"
        
        # Save file
        path = default_storage.save(filename, image)
        
        # Return URL
        return JsonResponse({
            'url': default_storage.url(path)
        })
    
    return JsonResponse({'error': 'No image provided'}, status=400)

@staff_member_required
def article_list_view(request):
    """
    View for listing and managing articles with advanced filtering and bulk actions
    """
    # Get query parameters
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)
    
    # Base queryset with optimized loading - removed tags
    articles = Article.objects.select_related(
        'category', 
        'created_by',
        'updated_by'
    ).order_by('-updated_at')
    
    # Apply filters
    if category_id:
        articles = articles.filter(category_id=category_id)
    if status:
        articles = articles.filter(status=status)
    if search:
        articles = articles.filter(
            Q(title__icontains=search) |
            Q(excerpt__icontains=search) |
            Q(content__icontains=search) |
            Q(meta_keywords__icontains=search)
        )
    
    # Get categories with counts for filter dropdown
    categories = ArticleCategory.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count')
    
    # Get counts for stats
    total_articles = Article.objects.count()
    published_count = Article.objects.filter(status='published').count()
    draft_count = Article.objects.filter(status='draft').count()
    featured_count = Article.objects.filter(is_featured=True).count()
    
    # Get recent articles for activity feed
    recent_articles = Article.objects.select_related(
        'updated_by'
    ).order_by('-updated_at')[:10]
    
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
        'featured_count': featured_count,
        'recent_articles': recent_articles,
        'selected_category': category_id,
        'selected_status': status,
        'search_query': search,
    }
    
    return render(request, 'admin/article_list.html', context)

@staff_member_required
@require_POST
def bulk_action_view(request):
    """
    Handle bulk actions on articles
    """
    action = request.POST.get('action')
    article_ids = request.POST.getlist('ids[]')
    
    if not article_ids:
        return JsonResponse({'error': 'No articles selected'}, status=400)
        
    articles = Article.objects.filter(id__in=article_ids)
    
    try:
        if action == 'delete':
            articles.delete()
            message = f'Successfully deleted {len(article_ids)} articles'
            
        elif action == 'publish':
            articles.update(
                status='published',
                published_at=timezone.now(),
                updated_by=request.user
            )
            message = f'Successfully published {len(article_ids)} articles'
            
        elif action == 'unpublish':
            articles.update(
                status='draft',
                updated_by=request.user
            )
            message = f'Successfully unpublished {len(article_ids)} articles'
            
        elif action == 'feature':
            articles.update(
                is_featured=True,
                updated_by=request.user
            )
            message = f'Successfully featured {len(article_ids)} articles'
            
        elif action == 'unfeature':
            articles.update(
                is_featured=False,
                updated_by=request.user
            )
            message = f'Successfully unfeatured {len(article_ids)} articles'
            
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
        return JsonResponse({'message': message})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def create_default_registration_page():
    """Create default registration page with standardized content blocks"""
    registration_page = Page.objects.create(
        title="Pendaftaran Mahasiswa Baru",
        slug="pendaftaran",
        template='registration.html',
        status=Page.PUBLISHED,
        metadata={
            'meta_description': 'Pendaftaran Mahasiswa Baru Matana University',
            'meta_keywords': 'pendaftaran matana, daftar kuliah, biaya kuliah'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Pendaftaran Mahasiswa Baru',
            'subtitle': 'Bergabunglah dengan Matana University untuk masa depan yang lebih baik',
            'background_image': '/static/images/registration-hero.jpg',
            'order': 1
        },
        {
            'identifier': 'alur_section',
            'title': 'Alur Pendaftaran',
            'items': [
                {
                    'title': 'Registrasi Online',
                    'description': 'Isi formulir pendaftaran online dengan data yang valid',
                    'icon': 'form'
                },
                {
                    'title': 'Upload Dokumen',
                    'description': 'Upload dokumen yang diperlukan (Ijazah, Transkrip, dll)',
                    'icon': 'upload'
                },
                {
                    'title': 'Pembayaran Registrasi',
                    'description': 'Lakukan pembayaran biaya pendaftaran',
                    'icon': 'payment'
                },
                {
                    'title': 'Tes Masuk',
                    'description': 'Ikuti tes potensi akademik dan wawancara',
                    'icon': 'test'
                }
            ],
            'order': 2
        },
        {
            'identifier': 'biaya_section',
            'title': 'Biaya Kuliah',
            'description': 'Investasi untuk pendidikan berkualitas',
            'items': [
                {
                    'title': 'S1 Informatika',
                    'description': 'Program Studi Informatika',
                    'items': [
                        'Registrasi: Rp. 2.500.000',
                        'Per Semester: Rp. 12.500.000'
                    ]
                },
                {
                    'title': 'S1 Manajemen',
                    'description': 'Program Studi Manajemen',
                    'items': [
                        'Registrasi: Rp. 2.500.000',
                        'Per Semester: Rp. 11.500.000'
                    ]
                }
            ],
            'order': 3
        },
        {
            'identifier': 'dokumen_section',
            'title': 'Dokumen yang Diperlukan',
            'items': [
                {
                    'title': 'Dokumen Wajib',
                    'items': [
                        'Scan Ijazah SMA/SMK/Sederajat',
                        'Scan Transkrip Nilai',
                        'Scan KTP',
                        'Pas Foto Terbaru',
                        'Surat Keterangan Sehat'
                    ]
                }
            ],
            'order': 4
        },
        {
            'identifier': 'contact_section',
            'title': 'Informasi Kontak',
            'description': 'Hubungi kami untuk informasi lebih lanjut',
            'items': [
                {
                    'title': 'Phone',
                    'description': '+62 21 1234567',
                    'icon': 'phone'
                },
                {
                    'title': 'WhatsApp',
                    'description': '+62 812 3456 7890',
                    'icon': 'whatsapp'
                },
                {
                    'title': 'Email',
                    'description': 'admissions@matanauniversity.ac.id',
                    'icon': 'envelope'
                }
            ],
            'order': 5
        }
    ]
    
    create_standardized_blocks(registration_page, default_blocks)
    return registration_page

def registration_view(request):
    """View for registration page"""
    try:
        registration_page = Page.objects.get(
            slug='pendaftaran',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        registration_page = create_default_registration_page()
    
    # Get content blocks
    blocks = {}
    for block in registration_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content
    
    context = {
        'page': registration_page,
        'meta': registration_page.metadata,
        'blocks': blocks  # Simplified - just send all blocks
    }
    
    return render(request, 'pages/registration.html', context)

@require_POST
def registration_submit(request):
    try:
        # Get form data
        data = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'birth_date': request.POST.get('birth_date'),
            'school': request.POST.get('school'),
            'major': request.POST.get('major'),
            'program': request.POST.get('program'),
            'address': request.POST.get('address'),
        }
        
        # Save to database (implement your model)
        registration = Registration.objects.create(**data)
        
        # Send confirmation email
        context = {
            'registration': registration,
            'program_name': dict(PROGRAM_CHOICES)[data['program']]
        }
        
        email_html = render_to_string('emails/registration_confirmation.html', context)
        email_text = render_to_string('emails/registration_confirmation.txt', context)
        
        send_mail(
            subject='Pendaftaran Matana University',
            message=email_text,
            from_email='noreply@matanauniversity.ac.id',
            recipient_list=[data['email']],
            html_message=email_html
        )
        
        messages.success(request, 'Pendaftaran berhasil! Silakan cek email Anda untuk informasi selanjutnya.')
        return redirect('registration_success')
        
    except Exception as e:
        messages.error(request, 'Terjadi kesalahan. Silakan coba lagi.')
        return redirect('registration')

def create_default_scholarship_page():
    """Create default scholarship page with standardized content blocks"""
    scholarship_page = Page.objects.create(
        title="Program Beasiswa",
        slug="beasiswa",
        template='scholarship.html',
        status=Page.PUBLISHED,
        metadata={
            'meta_description': 'Program Beasiswa Matana University - Wujudkan impian kuliah berkualitas',
            'meta_keywords': 'beasiswa matana, beasiswa kuliah, program beasiswa'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Wujudkan Impian',
            'subtitle': 'Kuliah di Matana',
            'description': 'Raih kesempatan mendapatkan beasiswa pendidikan di Matana University. Kami berkomitmen untuk mendukung mahasiswa berprestasi dalam menggapai masa depan yang lebih baik.',
            'badge_text': '🎓 Program Beasiswa 2024',
            'cta': [
                {
                    'text': 'Lihat Program Beasiswa',
                    'url': '#scholarship-programs',
                    'style': 'primary'
                },
                {
                    'text': 'Daftar Sekarang',
                    'url': '/pendaftaran',
                    'style': 'secondary'
                }
            ],
            'order': 1
        },
        {
            'identifier': 'stats_section',
            'items': [
                {
                    'number': '500+',
                    'label': 'Penerima Beasiswa Aktif'
                },
                {
                    'number': '12M+',
                    'label': 'Total Dana Beasiswa'
                },
                {
                    'number': '95%',
                    'label': 'Tingkat Kelulusan'
                }
            ],
            'order': 2
        },
        {
            'identifier': 'programs_section',
            'title': 'Pilihan Program Beasiswa',
            'subtitle': 'Program Beasiswa',
            'description': 'Kami menyediakan berbagai program beasiswa yang disesuaikan dengan prestasi dan kebutuhan mahasiswa',
            'items': [
            {
                'name': 'Beasiswa Akademik',
                'type': 'Unggulan',
                'description': 'Untuk siswa dengan prestasi akademik luar biasa',
                'benefits': [
                    'Potongan biaya kuliah hingga 100%',
                    'Tunjangan buku per semester',
                    'Prioritas program pertukaran pelajar'
                ]
            },
            {
                'name': 'Beasiswa Prestasi',
                'type': 'Khusus',
                'description': 'Untuk siswa berprestasi di bidang non-akademik',
                'benefits': [
                    'Potongan biaya kuliah hingga 75%',
                    'Dana pembinaan prestasi',
                    'Akses ke fasilitas khusus'
                ]
            },
            {
                'name': 'Beasiswa KIP Kuliah',
                'type': 'Pemerintah',
                'description': 'Program beasiswa dari pemerintah untuk mahasiswa kurang mampu',
                'benefits': [
                    'Biaya kuliah ditanggung penuh',
                    'Tunjangan bulanan',
                    'Bantuan biaya hidup'
                ]
            }
            ],
            'order': 3
        },
        {
            'identifier': 'requirements_section',
            'title': 'Persyaratan Umum Beasiswa',
            'subtitle': 'Persyaratan Program',
            'description': 'Pastikan Anda memenuhi semua persyaratan berikut sebelum mengajukan permohonan beasiswa',
            'categories': [
                {
                    'title': 'Persyaratan Akademik',
                    'icon': 'academic',
                    'items': [
                        'Nilai rata-rata rapor minimal 8.0',
                        'Peringkat 10 besar di kelas',
                        'Aktif dalam kegiatan ekstrakurikuler'
                    ]
                },
                {
                    'title': 'Dokumen Pendukung',
                    'icon': 'document',
                    'items': [
                        'Surat rekomendasi dari sekolah',
                        'Sertifikat prestasi akademik/non-akademik',
                        'Essay motivasi (500-1000 kata)'
                    ]
                },
                {
                    'title': 'Dokumen Finansial',
                    'icon': 'financial',
                    'items': [
                        'Slip gaji / penghasilan orang tua',
                        'Kartu Keluarga terbaru',
                        'Rekening listrik 3 bulan terakhir'
                    ]
                }
            ],
            'order': 4
        },
        {
            'identifier': 'timeline_section',
            'title': 'Proses Seleksi',
            'items': [
                {
                    'title': 'Pendaftaran Online',
                    'description': 'Isi formulir pendaftaran dan unggah dokumen yang diperlukan'
                },
                {
                    'title': 'Seleksi Berkas',
                    'description': 'Tim akan menyeleksi kelengkapan dan kesesuaian dokumen'
                },
                {
                    'title': 'Wawancara',
                    'description': 'Kandidat terpilih akan diundang untuk sesi wawancara'
                },
                {
                    'title': 'Pengumuman',
                    'description': 'Hasil seleksi akan diumumkan melalui email dan website'
                }
            ],
            'order': 5
        },
        {
            'identifier': 'cta_section',
            'title': 'Siap Untuk Mendaftar?',
            'description': 'Jangan lewatkan kesempatan untuk mendapatkan beasiswa di Matana University. Daftar sekarang dan wujudkan impianmu!',
            'cta': {
                'text': 'Daftar Beasiswa',
                'url': '/pendaftaran',
                'style': 'primary'
            },
            'order': 6
        }
    ]
    
    create_standardized_blocks(scholarship_page, default_blocks)
    return scholarship_page

def scholarship_view(request):
    """View for scholarship page"""
    try:
        logger.debug(f"Fetching scholarship page for request: {request.path}")
        scholarship_page = Page.objects.get(
            slug='beasiswa',
            status=Page.PUBLISHED
        )
        logger.info(f"Found existing scholarship page with ID: {scholarship_page.id}")
    except Page.DoesNotExist:
        logger.warning("Scholarship page not found, creating default page")
        scholarship_page = create_default_scholarship_page()
    
    try:
        # Get content blocks with error handling
        blocks = {}
        for block in scholarship_page.content_blocks.all().order_by('order'):
            try:
                blocks[block.identifier] = block.content
            except Exception as e:
                print(f"Error processing block {block.identifier}: {str(e)}")
                continue
        
        context = {
            'page': scholarship_page,
            'meta': scholarship_page.metadata,
            'blocks': blocks
        }
        
        
    except Exception as e:
        print(f"Error rendering scholarship page: {str(e)}")
        raise Http404("Page could not be rendered")
    return render(request, 'pages/scholarship.html', context)

@login_required
def article_save(request):
    try:
        article_id = request.POST.get('article_id')
        article = Article.objects.get(id=article_id) if article_id else Article()
        
        # Log untuk debugging
        print("Form data received:", request.POST)
        print("Featured image:", request.POST.get('featured_image'))
        
        # Update article fields
        article.title = request.POST.get('title')
        article.featured_image = request.POST.get('featured_image')
        article.excerpt = request.POST.get('excerpt')
        article.content = request.POST.get('content')
        article.category_id = request.POST.get('category')
        article.status = request.POST.get('status', 'draft')
        article.meta_description = request.POST.get('meta_description', '')
        article.meta_keywords = request.POST.get('meta_keywords', '')
        article.is_featured = request.POST.get('is_featured') == 'on'
        
        if not article_id:
            article.created_by = request.user
        article.updated_by = request.user
        
        # Generate slug if needed
        if not article.slug:
            article.slug = slugify(article.title)
        
        article.save()
        
        messages.success(request, 'Article saved successfully!')
        return redirect('article_edit', pk=article.id)
        
    except Exception as e:
        print("Error saving article:", str(e))
        messages.error(request, f'Error saving article: {str(e)}')
        return redirect('article_list')

def article_api_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return JsonResponse({
        'title': article.title,
        'featured_image': article.featured_image,
    })

@staff_member_required
def page_edit_view(request, slug):
    """API-based view for editing pages"""
    try:
        page = Page.objects.get(slug=slug)
    except Page.DoesNotExist:
        if slug == 'profil-matana':
            page = create_default_profile_page()
        elif slug == 'pendaftaran':
            page = create_default_registration_page()
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Page with slug "{slug}" not found.'
                }, status=404)
            messages.error(request, f'Page with slug "{slug}" not found.')
            return redirect('content_dashboard')

    if request.method == 'POST':
        try:
            # Validate and process the data
            if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid request method'
                }, status=400)

            # Parse and validate blocks data
            try:
                blocks_data = json.loads(request.POST.get('blocks', '{}'))
                if not isinstance(blocks_data, dict):
                    raise ValueError('Blocks data must be a dictionary')
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data for blocks'
                }, status=400)

            # Parse and validate metadata
            try:
                metadata = json.loads(request.POST.get('metadata', '{}'))
                if not isinstance(metadata, dict):
                    raise ValueError('Metadata must be a dictionary')
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data for metadata'
                }, status=400)

            # Update page metadata
            page.title = request.POST.get('title', page.title)
            page.metadata = metadata
            page.updated_at = timezone.now()
            page.save()

            # Update content blocks
            for identifier, content in blocks_data.items():
                try:
                    block = page.content_blocks.get(identifier=identifier)
                    
                    # Validate content structure
                    required_fields = ['title', 'description']
                    for field in required_fields:
                        if field not in content and field in block.content:
                            content[field] = block.content[field]
                    
                    # Ensure items is a list if present
                    if 'items' in content and not isinstance(content['items'], list):
                        content['items'] = []
                    
                    # Validate CTA structure
                    if 'cta' in content:
                        if not isinstance(content['cta'], dict):
                            content['cta'] = {}
                        for field in ['text', 'url', 'style']:
                            if field not in content['cta']:
                                content['cta'][field] = ''
                    
                    block.content = content
                    block.save()
                    
                except ContentBlock.DoesNotExist:
                    # Create new block if it doesn't exist
                    page.content_blocks.create(
                        identifier=identifier,
                        content_type=ContentBlock.RICH_TEXT,
                        content=content
                    )
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'Error processing block {identifier}: {str(e)}'
                    }, status=400)

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('page_list'),
                'message': 'Page updated successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error saving page: {str(e)}'
            }, status=500)

    # Get content blocks for initial form data
    blocks = {}
    for block in page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    context = {
        'page': page,
        'blocks': json.dumps(blocks),
        'title': f'Edit {page.title}',
        'subtitle': 'Update page content and settings'
    }
    
    return render(request, 'admin/page_form.html', context)

@staff_member_required
def page_list_view(request):
    """View for listing all pages"""
    pages = Page.objects.all().order_by('-updated_at')
    
    context = {
        'pages': pages,
        'title': 'Pages',
        'subtitle': 'Manage your website pages'
    }
    
    return render(request, 'admin/page_list.html', context)
