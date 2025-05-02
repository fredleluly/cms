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
from django.db import transaction
from .models import ProdiAdmin, ProgramStudi
from django.contrib.auth import logout
from django.views.decorators.cache import cache_page
from datetime import timedelta
from .models import ArticleReviewHistory
import mimetypes
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.views.decorators.http import require_safe
from django.template.response import TemplateResponse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .utils import superuser_required, safe_join_paths, get_file_details
from .models import DownloadToken
from .backup_utils import create_project_backup, get_project_size_estimation, check_available_space, DEFAULT_EXCLUDES
import threading
from apps.pages.utils import togglable_cache, clear_view_cache, CACHED_VIEWS_REGISTRY


# Get logger for this file
logger = logging.getLogger(__name__)

def custom_404(request, exception):

    return render(request, '404.html', status=404)

# views.py
from django.views.generic import TemplateView

class PedomanAkademikView(TemplateView):
    template_name = 'pages/pedoman_akademik.html'

class KalenderAkademikView(TemplateView):
    template_name = 'pages/kalender_akademik.html'

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
            'identifier': 'section1_mobile',
            'title': 'banner section',
            'subtitle': '',
            'items': [
                {
                    'title': 'banner1',
                    'image': '/static/images/banner_mob.jpg',
                },
                {
                    'title': 'banner2',
                    'image': '/static/images/banner_mob2.jpg',
                },
                {
                    'title': 'banner3',
                    'image': '/static/images/banner_mob3.jpg',
                },
                {
                    'title': 'banner4',
                    'image': '/static/images/banner_mob4.jpg',
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
            'title': 'Matana University Video Kampus',
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

def profile_view_lpm(request):
    return render(request, 'pages/profile_view_lpm.html')

def profile_view_lppm(request):
    return render(request, 'pages/profile_view_lppm.html')

@togglable_cache()
def home_view(request):
    try:
        page = Page.objects.get(is_homepage=True, status=Page.PUBLISHED)
    except Page.DoesNotExist :
        try:
            page = Page.objects.filter(status=Page.PUBLISHED).first()

            if page:
                page.is_homepage = True
                page.save()
            else:
                page = create_default_homepage()
                create_default_popup()
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
    today = timezone.now().date()
    berita_terbaru = Article.objects.filter(status='published', published_at__date__lte=today).order_by('-created_at')[:6]
    blocks['berita_terbaru'] = berita_terbaru
    
    # create_default_popup()

    context = {
        'page': page,
        'meta': page.metadata,
        'blocks': blocks, 
    }
    
    # Add popup context
    context.update(get_popup_context())
    print( " popup_active : ",context.get('popup_active'))
    
    return render(request, f'pages/{page.template}', context)

def get_popup_context():
    """Helper function to get popup blocks if the popup is active"""
    context = {}
    try:
        popup_page = Page.objects.get(slug='popup', status=Page.PUBLISHED)
        if popup_page.metadata.get('is_active', False):
            context['blocks_popup'] = {
                i.identifier: i.content 
                for i in popup_page.content_blocks.all().order_by('order')
            }
            context['popup_active'] = True
    except Page.DoesNotExist:
        pass
    return context

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
            'blocks': blocks
        }
        
        # Add popup context
        context.update(get_popup_context())
        
        template_name = f"pages/{page.template}.html"
        return render(request, template_name, context)
        
    except Exception as e:
        # Log the error and return a 500 error
        print(f"Error rendering page {slug}: {str(e)}")
        raise Http404("Page could not be rendered")

def create_default_mitra_page():
    """Create default mitra page if it doesn't exist"""
    mitra_page = Page.objects.create(
        title="Mitra Kerja Sama",
        slug="mitra",
        template='mitra.html',
        status=Page.PUBLISHED,
        metadata={
            'meta_description': 'Mitra Kerja Sama Matana University',
            'meta_keywords': 'mitra, matana university, universitas matana'
        }
    )

     
    default_blocks = [
        {
            'identifier': 'hospital_section',
            'title': 'Hospital',
                 'items': [
                {
                    'title': 'Rumah Sakit PUSB',
                    'image': '/static/images/mitra/h1.png',
                },
                {
                    'title': 'BETHSAIDA',
                    'image': '/static/images/mitra/h2.png',
                },
                {
                    'title': 'SERAPIMA',
                    'image': '/static/images/mitra/h3.png',
                },
                {
                    'title': 'RSUD',
                    'image': '/static/images/mitra/h4.png',
                },
                {
                    'title': 'The Rits-Carliton',
                    'image': '/static/images/mitra/h5.png',
                },
            ],
            'order': 1
        },
        {
            'identifier': 'hotel_section',
            'title': 'Hotel',
            'items': [
            
                {
                    'title': 'Hotel Santika',
                    'image': '/static/images/mitra/h6.png',
                },
                {
                    'title': 'The Rits-Carliton',
                    'image': '/static/images/mitra/h7.png',
                },
                {
                    'title': 'Hotel Santika',
                    'image': '/static/images/mitra/h8.png',
                },
                {
                    'title': 'The Rits-Carliton',
                    'image': '/static/images/mitra/h9.png',
                },
                {
                    'title': 'Hotel Santika',
                    'image': '/static/images/mitra/h10.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h11.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h12.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h13.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h14.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h15.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h16.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h17.png',
                },
                {
                    'title': 'Shangri-LA',
                    'image': '/static/images/mitra/h18.png',
                },
            ],
            'order': 2
        },{
            'identifier': 'institusi_section',
            'title': 'Institusi & Perusahaan',
            'items': [
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h19.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h20.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h21.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h22.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h23.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h24.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h25.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h26.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h27.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h28.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h29.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h30.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h31.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h32.png',
                },
            
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h34.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h35.png',
                },
                {
                    'title': 'PT. Paramount Group',
                    'image': '/static/images/mitra/h36.png',
                },
            ],
            'order': 3
        },{
            'identifier': 'universitas_section',
            'title': 'Universitas',
            'items': [
                {
                    'title': 'Universitas Indonesia',
                    'image': '/static/images/mitra/h37.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h38.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h39.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h40.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h41.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h42.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h43.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h44.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h45.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h46.png',
                },
                {
                    'title': 'Universitas Majada',
                    'image': '/static/images/mitra/h47.png',
                },
                {
                    'title': 'Universitas JIU',
                    'image': '/static/images/mitra/h48.png',
                }
            ],
            'order': 4
        },{
            'identifier': 'bank_section',
            'title': 'Bank',
            'items': [
                {
                    'title': 'BANK BNI',
                    'image': '/static/images/mitra/h49.png',
                },
                {
                    'title': 'BANK SOFT',
                    'image': '/static/images/mitra/h50.png',
                },
                {
                    'title': 'BANK IDX',
                    'image': '/static/images/mitra/h51.png',
                },
                {
                    'title': 'BANK SOFT',
                    'image': '/static/images/mitra/h52.png',
                },
                {
                    'title': 'BANK IDX',
                    'image': '/static/images/mitra/h53.png',
                },
            ],
            'order': 5
        }
    ]
    
    create_standardized_blocks(mitra_page, default_blocks)
    return mitra_page

@togglable_cache()
def mitra_view(request):
    """View for mitra page"""
    try:
        mitra_page = Page.objects.get(
            slug='mitra',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        mitra_page = create_default_mitra_page()
    
    # Get content blocks
    blocks = {}
    for block in mitra_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content
    
    context = {
        'page': mitra_page,
        'meta': mitra_page.metadata,
        'blocks': blocks, 'blocks_popup': { i.identifier: i.content for i in Page.objects.get(slug='popup', status=Page.PUBLISHED).content_blocks.all().order_by('order')  }  # Simplified - just send all blocks
    }
    
    return render(request, 'pages/mitra.html', context)

@staff_member_required
def cache_management_view(request):
    """
    View for managing the cache settings. Allows admin users to:
    1. Enable/disable caching globally
    2. Clear specific view caches or all caches
    3. See current cache status
    """
    try:
        # Handle form submissions
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'toggle_global':
                # Toggle global cache setting
                new_status = request.POST.get('cache_enabled') == 'true'
                
                # In a real application, you'd update an environment variable or a database setting
                # For this example, we'll just update the setting in memory (will reset on server restart)
                settings.CACHE_ENABLED = new_status
                
                messages.success(request, f"Global caching {'enabled' if new_status else 'disabled'}")
                
            elif action == 'clear_cache':
                # Clear specific view cache or all caches
                view_name = request.POST.get('view_name')
                if view_name and view_name != 'all':
                    success = clear_view_cache(view_name=view_name)
                else:
                    # Clear all caches
                    success = clear_view_cache()
                
                if success:
                    messages.success(request, f"Cache cleared for {'all views' if not view_name or view_name == 'all' else view_name}")
                else:
                    messages.error(request, "Failed to clear cache")
        
        # Get current cache status
        print('Debug: CACHE_ENABLED from settings:', getattr(settings, 'CACHE_ENABLED', False))
        
        cache_status = {
            'global_enabled': getattr(settings, 'CACHE_ENABLED', False) ,
            'timeout': getattr(settings, 'CACHE_TIMEOUT', 3600 * 24 * 2),
            'backend': settings.CACHES['default']['BACKEND'],
            'cacheable_views': [
                {
                    'name': name,
                    'description': info['description'],
                    'timeout': info['timeout']
                } 
                for name, info in CACHED_VIEWS_REGISTRY.items()
            ]
        }
        
        # Get popup status
        try:
            popup_page = Page.objects.get(slug='popup', status=Page.PUBLISHED)
            popup_status = popup_page.metadata.get('is_active', False)
        except Page.DoesNotExist:
            popup_status = False
        
        print('Debug: cache_status[global_enabled]:', cache_status['global_enabled'])
        
        # Add stats about cache usage if possible
        if hasattr(cache, 'info'):
            try:
                cache_status['stats'] = cache.info()
            except:
                cache_status['stats'] = None
        
        return render(request, 'admin/cache_management.html', {
            'cache_status': cache_status,
            'title': 'Cache Management',
            'popup_status': popup_status
        })
    except Exception as e:
        logger.error(f"Error in cache_management_view: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('admin:index')



@togglable_cache()
def news_view(request):
    # Get query parameters with defaults
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('search', '').strip()
    page_number = request.GET.get('page', 1)
    
    # Get current date
    today = timezone.now().date()
    
    # Base queryset with select_related for performance
    articles = Article.objects.select_related('category', 'created_by').filter(
        status='published',
        published_at__date__lte=today  # Only show articles with publication date today or earlier
    )
    
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
        article_count=Count('articles', filter=Q(articles__status='published', articles__published_at__date__lte=today))
    )
    
    context = {
        'featured_article': featured_article,
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'total_articles': total_count,
    }
    
    # Add popup context
    context.update(get_popup_context())
    
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
    
    # Add popup context
    context.update(get_popup_context())
    
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
    """
    View for creating new articles. Only accessible by superusers and article program admins.
    """
    # Check if user has article program studi permission
    if not request.user.is_superuser:
        try:
            prodi_admin = ProdiAdmin.objects.get(user=request.user)
            is_article_admin = prodi_admin.program_studi.filter(slug='article').exists()
            if not is_article_admin:
                messages.error(request, 'Anda tidak memiliki izin untuk membuat artikel.')
                return redirect('content_dashboard')
        except ProdiAdmin.DoesNotExist:
            messages.error(request, 'Anda tidak memiliki izin untuk membuat artikel.')
            return redirect('content_dashboard')
    
    form = ArticleForm()
    categories = ArticleCategory.objects.all()
    
    context = {
        'form': form,
        'categories': categories,
        'action': 'create',
        'title': 'Create New Article',
        'now': timezone.now()  # Add current time to context
    }
    return render(request, 'admin/article_form.html', context)

@staff_member_required
def article_edit_view(request, pk):

    # Check if user has article program studi permission
    if not request.user.is_superuser:
        try:
            prodi_admin = ProdiAdmin.objects.get(user=request.user)
            is_article_admin = prodi_admin.program_studi.filter(slug='article').exists()
            if not is_article_admin:
                messages.error(request, 'Anda tidak memiliki izin untuk mengedit artikel.')
                return redirect('content_dashboard')
        except ProdiAdmin.DoesNotExist:
            messages.error(request, 'Anda tidak memiliki izin untuk mengedit artikel.')
            return redirect('content_dashboard')
        

    article = get_object_or_404(Article, pk=pk)
    form = ArticleForm(instance=article)
    categories = ArticleCategory.objects.all()
    context = {
        'form': form,
        'article': article,
        'categories': categories,
        'action': 'edit',
        'title': f'Edit Article: {article.title}',
        'now': timezone.now()  # Add current time to context
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

    try:
        with transaction.atomic():
            article_id = request.POST.get('article_id')
            
            if article_id:
                article = get_object_or_404(Article, id=article_id)
                # Check if user can edit this article
                if not article.can_edit(request.user):
                    messages.error(request, 'You do not have permission to edit this article.')
                    return redirect('content_dashboard')
            else:
                article = Article(created_by=request.user)
            
            # Validate required fields
            required_fields = ['title', 'excerpt', 'content', 'category']
            for field in required_fields:
                if not request.POST.get(field):
                    messages.error(request, f'{field.title()} is required.')
                    return redirect('article_edit' if article_id else 'article_create')
            
            # Update basic fields
            article.featured_image = request.POST.get('featured_image')
            article.title = request.POST.get('title')
            article.slug = request.POST.get('slug') or slugify(article.title)
            article.category_id = request.POST.get('category')
            article.excerpt = request.POST.get('excerpt')
            article.content = request.POST.get('content')
            article.meta_description = request.POST.get('meta_description')
            article.meta_keywords = request.POST.get('meta_keywords')
            article.is_featured = request.POST.get('is_featured') == 'on'
            
            # Store any scheduled publication date from form
            scheduled_date = None
            published_at_str = request.POST.get('published_at')
            if published_at_str:
                try:
                    # Try multiple formats to handle browser differences
                    for format_str in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M']:
                        try:
                            scheduled_date = timezone.make_aware(
                                datetime.strptime(published_at_str, format_str),
                                timezone.get_current_timezone()
                            )
                            break
                        except ValueError:
                            continue
                            
                    # If we found a valid date, keep it for later
                    if scheduled_date:
                        article.published_at = scheduled_date
                except Exception as e:
                    logger.error(f"Error parsing published_at date: {str(e)}")
            
            # Handle status changes
            new_status = request.POST.get('status')
            old_status = article.status
            
            # Handle resubmission of rejected articles
            if request.POST.get('resubmit') and article.status == 'rejected':
                if article.created_by != request.user:
                    messages.error(request, 'Only the original author can resubmit a rejected article.')
                    return redirect('content_dashboard')
                article.status = 'pending'
                article.review_comment = None
                article.reviewed_by = None
                article.reviewed_at = None
                messages.success(request, 'Article has been resubmitted for review.')
            
            # Handle status changes by superuser
            elif request.user.is_superuser and new_status:
                if new_status not in dict(Article.STATUS_CHOICES):
                    messages.error(request, 'Invalid status.')
                    return redirect('article_edit' if article_id else 'article_create')
                
                article.status = new_status
                
                # Only set published_at automatically if:
                # 1. There is no scheduled date from the form, AND
                # 2. There is no existing published_at date, AND
                # 3. The status is being set to published
                if new_status == 'published' and not scheduled_date and not article.published_at:
                    article.published_at = timezone.now()
                elif new_status == 'rejected':
                    article.review_comment = request.POST.get('review_comment')
                    article.reviewed_by = request.user
                    article.reviewed_at = timezone.now()
                
                # Create review history entry
                if old_status != new_status:
                    ArticleReviewHistory.objects.create(
                        article=article,
                        status=new_status,
                        comment=request.POST.get('review_comment'),
                        reviewed_by=request.user
                    )
            
            # For non-superusers updating published articles
            elif article.status == 'published' and not request.user.is_superuser:
                # Set status back to pending for review
                article.status = 'pending'
                article.review_comment = None
                article.reviewed_by = None
                article.reviewed_at = None
                messages.success(request, 'Your changes have been submitted for review.')
                
                # Create review history entry
                ArticleReviewHistory.objects.create(
                    article=article,
                    status='pending',
                    comment='Article update submitted for review',
                    reviewed_by=request.user
                )
            
            # For non-superusers creating new articles
            elif not request.user.is_superuser:
                article.status = 'pending'
            
            article.updated_by = request.user
            article.save()
            
            # If this is a scheduled publication, make sure the date is preserved
            if scheduled_date and scheduled_date > timezone.now():
                # Force update with direct database query to bypass model save logic
                Article.objects.filter(id=article.id).update(published_at=scheduled_date)
                # Refresh to get updated values
                article.refresh_from_db()
                
                if article.status == 'published':
                    messages.success(request, f'Article "{article.title}" has been scheduled for publication on {scheduled_date.strftime("%B %d, %Y at %H:%M")}.')
                else:
                    messages.success(request, f'Article "{article.title}" has been saved successfully.')
            else:
                messages.success(request, f'Article "{article.title}" has been saved successfully.')
                
            return redirect('content_dashboard')
            
    except Exception as e:
        messages.error(request, f'Error saving article: {str(e)}')
        return redirect('article_edit' if article_id else 'article_create')

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
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/Gedung.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Menjadi Perguruan Tinggi terpercaya dan terkemuka dalam akademik dan profesionalisme yang berwawasan nasional dan internasional, berperan dalam peningkatan kualitas iman kepercayaan, ilmu pengetahuan dan teknologi, yang merupakan karunia Tuhan, untuk kecerdasan dan kesejahteraan umat manusia serta kehidupan yang lebih baik dan berkelanjutan.'
                },
                {
                    'title': 'Misi',
                    'description': "a. Terbentuknya lulusan yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih;\nb.Terciptanya lulusan yang memiliki kemampuan penelitian, kreativitas, inovasi, dan berjiwa kewirausahaan;\nc. Terbentuknya generasi penerus yang memiliki kepedulian untuk kehidupan berkelanjutan."
                }
            ],
            'order': 2
        },
        {
            'identifier': 'sejarah_section',
            'title': 'Sejarah',
            'description': 'Universitas Matana mulai beroperasi pada bulan Agustus 2014, berlokasi di Matana University Tower dengan 10 Program Studi. Universitas Matana mendidik calon-calon eksekutif bisnis dan pemimpin masa depan dalam berbagai bidang ilmu, dengan memberi penekanan yang seimbang antara pengetahuan akademik, pengembangan kemampuansoft skills dan pembentukan karakter mahasiswa yang bersifat menyeluruh, sehingga lulusan Universitas Matana adalah sarjana yang menguasai pengetahuan dan keterampilan tertentu dan memiliki INTEGRITAS (INTEGRITY) yaitu keterpaduan antara keyakinan, pemikiran, kata dan tindakan; dan PENATALAYANAN (STEWARDSHIP) untuk memenuhi komitmen dalam pencarian, pengembangan, penggunaan waktu dan aset yang dipercayakan Tuhan dengan penuh tanggung jawab dan integritas untuk melayani sesama; serta SALING MENGHARGAI (RESPECT) terhadap pemangku kepentingan dalam semangat integritas dan pelayanan.\n\nKarena itu, seluruh pengalaman akademik mahasiswa difokuskan bagi aktualisasi kapasitas belajar yaitu kapasitas intelektual, sosial, entreprenurial, dan, spiritual. Sarjana Matana adalah manusia terdidik dan terampil karena selain memiiki budaya research dan keilmuan, juga seimbang dengan nilai moral dan ketaatan kepada Tuhan.\n\nProses pembelajaran yang evidence-driven adalah karakteristik khusus Universitas Matana, dimana mahasiswa dan dosen akan berkolaborasi dalam pembelajaran berbasis-penelitian atau research-based-teaching and learning (RBTL) untuk mengkonstruksi pengetahuan dan keterampilan bukan menghafal konten buku-teks. Proses pembelajaran di Universitas Matana tidak hanya mengembangkan kemampuan akademik. Mahasiswa juga dibekali dengan sertifikat kompetensi keterampilan tertentu selama masa kuliah berlangsung, sehingga dapat mereka pergunakan untuk bekerja sambil kuliah atau memudahkan lulusan memperoleh pekerjaan segera saat mereka lulus.\n\nProses dalam mengintegrasikan tridharma Perguruan Tinggi mampu dilakukan, karena ditopang secara integratif oleh Pusat Pengembangan Sistem Pembelajaran, Pusat Studi Keilmuan, Pusat Pengembangan Ilmu dan Pemanfaatan IPTEKS, Pusat Pengembangan dan Pemberdayaan Masyarakat serta Pusat Pendidikan Vokasi.\n\nDalam proses pembelajaran apabila mahasiswa belum mampu mencapai prestasi yang diharapkan setiap semester, mereka akan dibantu secara profesional oleh Pusat Bimbingan dan Konseling untuk dibantu, dibimbing dan diarahkan agar mahasiswa mampu mengatasi kendala yang mengganggu capaian pembelajarannya, serta penguatan motivasi mahasiswa sehingga dapat mengejar ketertinggalannya.\n\nBagi Universitas Matana, mahasiswa adalah insan potensial dan aset sosial yang harus dikembangkan dan di dorong menjadi manusia yang berintegritas, melayani, dan menghargai manusia dan kemanusiaan. Kami menghargai setiap individu yang bergabung di Universitas Matana sebagai pribadi yang special dan layak mendapatkan yang terbaik. Mari bergabung ke tempat yang tepat demi masa depan anda. Kami menyambut anda dalam keluarga besar Universitas Matana',
            'order': 4
        },
        {
            'identifier': 'keunggulan_section',
            'title': 'Keunggulan Matana',
            'items': [
                {
                    'title': 'Menerapkan kurikulum akademik yang mendukung lulusan siap berkompetisi di dunia kerja',
                },
                {
                    'title': 'Dosen yang profesional dan berprestasi di dalam dan luar negeri',
                },
                {
                    'title': 'Unit Kegiatan Mahasiswa (UKM) yang berprestasi di nasional dan internasional',
                },
                {
                    'title': 'Memiliki fasilitas yang mendkung praktik setiap program studi',
                },
                {
                    'title': 'Memiliki program Student Exchange (pertukaran mahasiswa) ke universitas ternama di Asia dan Eropa',
                },
                {
                    'title': 'Kesempatan berkarir di jajaran mitra bisnis Matana University',
                },
                {
                    'title': 'Lokasi kampus strategis, berlokasi di sentra bisnis Gading Serpong',
                },
            ],
            'order': 5
        },   {
            'identifier': 'fasilitas_section',
            'title': 'Fasilitas Matana',
            'items': [
                {
                    'title': 'Lab Akutansi',
                    'image': '/static/images/fas1.jpg',
                },
                {
                    'title': 'Lab iMac',
                    'image': '/static/images/fas2.jpg',
                },
                {
                    'title': 'Lab Mobile Game',
                    'image': '/static/images/fas3.jpg',
                },
                {
                    'title': 'Lab Statistika',
                    'image': '/static/images/fas1.jpg',
                },
            ],
         
            'order': 6
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

# Prodi FEBIS
# Manajemen
def create_default_profile_page_manajemen():
    """Create default profile page with standardized content blocks"""
    try:
        prodi = ProgramStudi.objects.get(slug='manajemen')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="Manajemen",
        slug="prodi-manajemen",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Profil Matana University - Perguruan tinggi terpercaya dan terkemuka',
            'meta_keywords': 'profil matana, visi misi matana, sejarah matana'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 MANAJEMEN',
            'background_image': '/static/images/informatika.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/hospar.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Menjadi Perguruan Tinggi terpercaya dan terkemuka dalam akademik dan profesionalisme yang berwawasan nasional dan internasional, berperan dalam peningkatan kualitas iman kepercayaan, ilmu pengetahuan dan teknologi, yang merupakan karunia Tuhan, untuk kecerdasan dan kesejahteraan umat manusia serta kehidupan yang lebih baik dan berkelanjutan.'
                },
                {
                    'title': 'Misi',
                    'description': "- Terbentuknya Sarjana Manajemen yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih.\n- Terciptanya Sarjana Manajemen yang memiliki kemampuan penelitian, kreativitas, inovasi, dan berjiwa kewirausahaan.\n- Terbentuknya generasi penerus yang memiliki kepedulian untuk kehidupan berkelanjutan."
                }
            ],
            'order': 2
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': 'Universitas Matana mulai beroperasi pada bulan Agustus 2014, berlokasi di Matana University Tower dengan 10 Program Studi. Universitas Matana mendidik calon-calon eksekutif bisnis dan pemimpin masa depan dalam berbagai bidang ilmu, dengan memberi penekanan yang seimbang antara pengetahuan akademik, pengembangan kemampuansoft skills dan pembentukan karakter mahasiswa yang bersifat menyeluruh, sehingga lulusan Universitas Matana adalah sarjana yang menguasai pengetahuan dan keterampilan tertentu dan memiliki INTEGRITAS (INTEGRITY) yaitu keterpaduan antara keyakinan, pemikiran, kata dan tindakan; dan PENATALAYANAN (STEWARDSHIP) untuk memenuhi komitmen dalam pencarian, pengembangan, penggunaan waktu dan aset yang dipercayakan Tuhan dengan penuh tanggung jawab dan integritas untuk melayani sesama; serta SALING MENGHARGAI (RESPECT) terhadap pemangku kepentingan dalam semangat integritas dan pelayanan.\n\nKarena itu, seluruh pengalaman akademik mahasiswa difokuskan bagi aktualisasi kapasitas belajar yaitu kapasitas intelektual, sosial, entreprenurial, dan, spiritual. Sarjana Matana adalah manusia terdidik dan terampil karena selain memiiki budaya research dan keilmuan, juga seimbang dengan nilai moral dan ketaatan kepada Tuhan.\n\nProses pembelajaran yang evidence-driven adalah karakteristik khusus Universitas Matana, dimana mahasiswa dan dosen akan berkolaborasi dalam pembelajaran berbasis-penelitian atau research-based-teaching and learning (RBTL) untuk mengkonstruksi pengetahuan dan keterampilan bukan menghafal konten buku-teks. Proses pembelajaran di Universitas Matana tidak hanya mengembangkan kemampuan akademik. Mahasiswa juga dibekali dengan sertifikat kompetensi keterampilan tertentu selama masa kuliah berlangsung, sehingga dapat mereka pergunakan untuk bekerja sambil kuliah atau memudahkan lulusan memperoleh pekerjaan segera saat mereka lulus.\n\nProses dalam mengintegrasikan tridharma Perguruan Tinggi mampu dilakukan, karena ditopang secara integratif oleh Pusat Pengembangan Sistem Pembelajaran, Pusat Studi Keilmuan, Pusat Pengembangan Ilmu dan Pemanfaatan IPTEKS, Pusat Pengembangan dan Pemberdayaan Masyarakat serta Pusat Pendidikan Vokasi.\n\nDalam proses pembelajaran apabila mahasiswa belum mampu mencapai prestasi yang diharapkan setiap semester, mereka akan dibantu secara profesional oleh Pusat Bimbingan dan Konseling untuk dibantu, dibimbing dan diarahkan agar mahasiswa mampu mengatasi kendala yang mengganggu capaian pembelajarannya, serta penguatan motivasi mahasiswa sehingga dapat mengejar ketertinggalannya.\n\nBagi Universitas Matana, mahasiswa adalah insan potensial dan aset sosial yang harus dikembangkan dan di dorong menjadi manusia yang berintegritas, melayani, dan menghargai manusia dan kemanusiaan. Kami menghargai setiap individu yang bergabung di Universitas Matana sebagai pribadi yang special dan layak mendapatkan yang terbaik. Mari bergabung ke tempat yang tepat demi masa depan anda. Kami menyambut anda dalam keluarga besar Universitas Matana',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {
                    'title': 'Digital Marketing',
                },
                {
                    'title': 'Human Capital',
                },
                {
                    'title': 'Investment',
                },
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {
                    'title': 'Religion'
                },
                {
                    'title': 'English'
                },
                {
                    'title': 'Indonesian'
                },
                {
                    'title': 'Academic Writing'
                },
                {
                    'title': 'Critical Thinking'
                },
                {
                    'title': 'Economics'
                },
                {
                    'title': 'Business Mathematics'
                },
                {
                    'title': 'Business Technology'
                },
                {
                    'title': 'Basic Accounting'
                },
                {
                    'title': 'Statistics'
                },
                {
                    'title': 'Finance'
                },
                {
                    'title': 'Marketing'
                },
                {
                    'title': 'Human Resource Management'
                },
                {
                    'title': 'Strategic Management'
                },
                {
                    'title': 'Research Method'
                },
                {
                    'title': 'Innovation'
                },
                {
                    'title': 'Decision Making Theory'
                },
                {
                    'title': 'International Business'
                },
                {
                    'title': 'Taxation'
                },
                {
                    'title': 'Entrepreneurship'
                },
                {
                    'title': 'Leadership'
                },
                {
                    'title': 'Financial Institutions'
                },
                {
                    'title': 'Consumer Behavior'
                },
                {
                    'title': 'Business Communication'
                }
            ],
         
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {
                'title': 'Digital Marketing Specialist'
                },
                {
                    'title': 'Marketing Communication Specialist'
                },
                {
                    'title': 'Organizational Development Specialist'
                },
                {
                    'title': 'Financial Analyst'
                },
                {
                    'title': 'Content/Creative Creator'
                },
                {
                    'title': 'Risk Management Associate'
                },
                {
                    'title': 'Human Capital Specialist'
                },
                {
                    'title': 'S1 Manajemen'
                }
            ],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_manajemen(request):
    """View for profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-manajemen',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_manajemen()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('manajemen')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'manajemen'
    }
    
    return render(request, 'pages/prodi.html', context)
# Prodi FEBIS
# Manajemen
def create_default_profile_page_manajemens2():
    """Create default profile page with standardized content blocks"""
    try:
        prodi = ProgramStudi.objects.get(slug='manajemen')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="Magister Manajemen",
        slug="prodi-manajemens2",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Profil Matana University - Perguruan tinggi terpercaya dan terkemuka',
            'meta_keywords': 'profil matana, visi misi matana, sejarah matana'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Magister Manajemen',
            'background_image': '/static/images/informatika.jpg',
            'order': 1 ,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/hospar.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Menjadi Perguruan Tinggi terpercaya dan terkemuka dalam akademik dan profesionalisme yang berwawasan nasional dan internasional, berperan dalam peningkatan kualitas iman kepercayaan, ilmu pengetahuan dan teknologi, yang merupakan karunia Tuhan, untuk kecerdasan dan kesejahteraan umat manusia serta kehidupan yang lebih baik dan berkelanjutan.'
                },
                {
                    'title': 'Misi',
                    'description': "- Terbentuknya Sarjana Manajemen yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih.\n- Terciptanya Sarjana Manajemen yang memiliki kemampuan penelitian, kreativitas, inovasi, dan berjiwa kewirausahaan.\n- Terbentuknya generasi penerus yang memiliki kepedulian untuk kehidupan berkelanjutan."
                }
            ],
            'order': 2
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': 'Universitas Matana mulai beroperasi pada bulan Agustus 2014, berlokasi di Matana University Tower dengan 10 Program Studi. Universitas Matana mendidik calon-calon eksekutif bisnis dan pemimpin masa depan dalam berbagai bidang ilmu, dengan memberi penekanan yang seimbang antara pengetahuan akademik, pengembangan kemampuansoft skills dan pembentukan karakter mahasiswa yang bersifat menyeluruh, sehingga lulusan Universitas Matana adalah sarjana yang menguasai pengetahuan dan keterampilan tertentu dan memiliki INTEGRITAS (INTEGRITY) yaitu keterpaduan antara keyakinan, pemikiran, kata dan tindakan; dan PENATALAYANAN (STEWARDSHIP) untuk memenuhi komitmen dalam pencarian, pengembangan, penggunaan waktu dan aset yang dipercayakan Tuhan dengan penuh tanggung jawab dan integritas untuk melayani sesama; serta SALING MENGHARGAI (RESPECT) terhadap pemangku kepentingan dalam semangat integritas dan pelayanan.\n\nKarena itu, seluruh pengalaman akademik mahasiswa difokuskan bagi aktualisasi kapasitas belajar yaitu kapasitas intelektual, sosial, entreprenurial, dan, spiritual. Sarjana Matana adalah manusia terdidik dan terampil karena selain memiiki budaya research dan keilmuan, juga seimbang dengan nilai moral dan ketaatan kepada Tuhan.\n\nProses pembelajaran yang evidence-driven adalah karakteristik khusus Universitas Matana, dimana mahasiswa dan dosen akan berkolaborasi dalam pembelajaran berbasis-penelitian atau research-based-teaching and learning (RBTL) untuk mengkonstruksi pengetahuan dan keterampilan bukan menghafal konten buku-teks. Proses pembelajaran di Universitas Matana tidak hanya mengembangkan kemampuan akademik. Mahasiswa juga dibekali dengan sertifikat kompetensi keterampilan tertentu selama masa kuliah berlangsung, sehingga dapat mereka pergunakan untuk bekerja sambil kuliah atau memudahkan lulusan memperoleh pekerjaan segera saat mereka lulus.\n\nProses dalam mengintegrasikan tridharma Perguruan Tinggi mampu dilakukan, karena ditopang secara integratif oleh Pusat Pengembangan Sistem Pembelajaran, Pusat Studi Keilmuan, Pusat Pengembangan Ilmu dan Pemanfaatan IPTEKS, Pusat Pengembangan dan Pemberdayaan Masyarakat serta Pusat Pendidikan Vokasi.\n\nDalam proses pembelajaran apabila mahasiswa belum mampu mencapai prestasi yang diharapkan setiap semester, mereka akan dibantu secara profesional oleh Pusat Bimbingan dan Konseling untuk dibantu, dibimbing dan diarahkan agar mahasiswa mampu mengatasi kendala yang mengganggu capaian pembelajarannya, serta penguatan motivasi mahasiswa sehingga dapat mengejar ketertinggalannya.\n\nBagi Universitas Matana, mahasiswa adalah insan potensial dan aset sosial yang harus dikembangkan dan di dorong menjadi manusia yang berintegritas, melayani, dan menghargai manusia dan kemanusiaan. Kami menghargai setiap individu yang bergabung di Universitas Matana sebagai pribadi yang special dan layak mendapatkan yang terbaik. Mari bergabung ke tempat yang tepat demi masa depan anda. Kami menyambut anda dalam keluarga besar Universitas Matana',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {
                    'title': 'Digital Marketing',
                },
                {
                    'title': 'Human Capital',
                },
                {
                    'title': 'Investment',
                },
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {
                    'title': 'Religion'
                },
                {
                    'title': 'English'
                },
                {
                    'title': 'Indonesian'
                },
                {
                    'title': 'Academic Writing'
                },
                {
                    'title': 'Critical Thinking'
                },
                {
                    'title': 'Economics'
                },
                {
                    'title': 'Business Mathematics'
                },
                {
                    'title': 'Business Technology'
                },
                {
                    'title': 'Basic Accounting'
                },
                {
                    'title': 'Statistics'
                },
                {
                    'title': 'Finance'
                },
                {
                    'title': 'Marketing'
                },
                {
                    'title': 'Human Resource Management'
                },
                {
                    'title': 'Strategic Management'
                },
                {
                    'title': 'Research Method'
                },
                {
                    'title': 'Innovation'
                },
                {
                    'title': 'Decision Making Theory'
                },
                {
                    'title': 'International Business'
                },
                {
                    'title': 'Taxation'
                },
                {
                    'title': 'Entrepreneurship'
                },
                {
                    'title': 'Leadership'
                },
                {
                    'title': 'Financial Institutions'
                },
                {
                    'title': 'Consumer Behavior'
                },
                {
                    'title': 'Business Communication'
                }
            ],
         
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {
                'title': 'Digital Marketing Specialist'
                },
                {
                    'title': 'Marketing Communication Specialist'
                },
                {
                    'title': 'Organizational Development Specialist'
                },
                {
                    'title': 'Financial Analyst'
                },
                {
                    'title': 'Content/Creative Creator'
                },
                {
                    'title': 'Risk Management Associate'
                },
                {
                    'title': 'Human Capital Specialist'
                },
                {
                    'title': 'S1 Manajemen'
                }
            ],
            'order': 7
        },
        {
            'identifier': 'major_badge_section',
            'title': 'Program Magister',
            'order': 8
        }
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_manajemens2(request):
    """View for profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-manajemens2',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_manajemens2()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('manajemens')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'manajemens2'
    }
    
    return render(request, 'pages/prodi.html', context)

# Akuntansi
def create_default_profile_page_akuntansi():
    """Create default profile page with standardized content blocks for Akuntansi"""
    try:
        prodi = ProgramStudi.objects.get(slug='akutansi')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="Akuntansi",
        slug="prodi-akuntansi",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi Akuntansi Matana University - Terpercaya dan terkemuka dalam bidang audit, perpajakan, dan digital akuntansi',
            'meta_keywords': 'akuntansi matana, audit, perpajakan, digital akuntansi'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 AKUNTANSI',
            'background_image': '/static/images/hospar.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi Akuntansi',
            'description': 'Program Studi Akuntansi Matana University dirancang bagi mahasiswa untuk mampu mengkomunikasikan informasi keuangan dan operasional kepada para pengambil keputusan, baik pada organisasi bisnis, organisasi pemerintah, maupun organisasi nirlaba. Informasi keuangan ini akan membantu para pengambil keputusan untuk kepentingan pengendalian operasi bisnis, perencanaan dan pengendalian pajak, penganggaran bisnis maupun penganggaran pemerintah, serta analisis kinerja dan pelaporan keuangan kepada para pemangku kepentingan(stakeholders).',
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/architecture.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Menjadi Program Studi Akuntansi dalam bidang audit, perpajakan, dan digital akuntansi yang terpercaya dan terkemuka dalam bidang akademik dan profesional serta berwawasan nasional dan internasional, berperan dalam peningkatan kualitas iman kepercayaan, ilmu pengetahuan dan teknologi, yang merupakan Karunia Hikmat Tuhan, untuk kecerdasan dan kesejahteraan umat manusia serta kehidupan yang berkelanjutan.'
                },
                {
                    'title': 'Misi',
                    'description': "1. Terbentuknya Sarjana Akuntansi yang berkualitas dan memiliki kemampuan akademik secara profesional dalam bidang audit, perpajakan, dan digital akuntansi, serta berwawasan nasional maupun internasional.\n2. Terbentuknya Sarjana Akuntansi dalam bidang audit, perpajakan, dan digital akuntansi yang memiliki nilai-nilai Integritas (Integrity) – Penatalayanan (Stewardship) – Respek (Respect), yang berlandaskan iman kepercayaan.\n3. Terbentuknya Sarjana Akuntansi dalam bidang audit, perpajakan, dan digital akuntansi yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih.\n4. Terciptanya Sarjana Akuntansi dalam bidang audit, perpajakan, dan digital akuntansi yang memiliki kompetensi penelitian, kreativitas, inovasi dan menguasai teknologi akuntansi.\n5. Terbentuknya generasi penerus menjadi Sarjana Akuntansi yang ahli dalam bidang audit, perpajakan, dan digital akuntansi yang berjiwa entrepreneur serta memiliki kepedulian untuk kehidupan berkelanjutan di masyarakat."
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': '1. Menghasilkan Sarjana Akuntansi yang memiliki kompetensi dalam bidang keahlian: audit, perpajakan, dan digital akuntansi yang penuh kasih, berintegritas, profesional, inovatif, berjiwa enterpreuner dan mampu bersaing serta berkiprah dalam dunia bisnis nasional dan internasional.\n2. Menghasilkan Sarjana Akuntansi yang mampu dan terlatih dalam melaksanakan penelitian serta implementasi melalui publikasi untuk kemajuan ilmu pengetahuan dan teknologi di bidang audit, perpajakan, dan digital akuntansi dalam meningkatkan kualitas kehidupan masyarakat.\n3. Menghasilkan Sarjana Akuntansi yang mampu menerapkan pengabdian kepada masyarakat sebagai aktualisasi dan penerapan ilmu pengetahuan dalam bidang audit, perpajakan, dan digital akuntansi sebagai bentuk kepedulian atas kehidupan masyarakat yang berkelanjutan.\n4. Menghasilkan lulusan Sarjana Akuntansi dalam bidang audit, perpajakan, dan digital akuntansi yang berjiwa entrepreneur dan mampu mengintegrasikan kesadaran akan Ketuhanan, kemanusiaan, kenegarawanan, dan lingkungan.\n5. Memperkuat dan menyebarluaskan karya ilmiah akuntansi kepada masyarakat dalam bidang audit, perpajakan, dan digital akuntansi yang bercirikan nilai lokal, nasional dan internasional.',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'Taxation'},
                {'title': 'Auditing'},
                {'title': 'Digital Accounting'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {'title': 'Basic Accounting'},
                {'title': 'Basic Tax'},
                {'title': 'Cost Accounting'},
                {'title': 'Data Based System'},
                {'title': 'Religion'},
                {'title': 'English'},
                {'title': 'Indonesian'},
                {'title': 'Entrepreneurship'},
                {'title': 'Financial Accounting'},
                {'title': 'Intermediate Financial Accounting'},
                {'title': 'Accounting Information System & Internal Control'},
                {'title': 'Auditing Management Accounting'},
                {'title': 'Accounting Theory'},
                {'title': 'Enterprise Resource Planning (ERP)'},
                {'title': 'Accounting Research Methodology'},
                {'title': 'Advance Financial Accounting'},
                {'title': 'International Financial Reporting Standard'},
                {'title': 'Analysis and Design of Information Accounting System'},
                {'title': 'Business Statistics'},
                {'title': 'Financial Institution and Money Market'},
                {'title': 'Strategic Management'},
                {'title': 'Financial Management'},
                {'title': 'Economics Theory'},
            ],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {'title': 'Auditor internal dan eksternal di perusahaan, BUMN, perbankan, dll'},
                {'title': 'Auditor Pajak di semua sektor industri'},
                {'title': 'Manajer Akuntansi'},
                {'title': 'Konsultan Pajak'},
                {'title': 'Akuntan'},
                {'title': 'Akuntan Manajemen'},
                {'title': 'Akuntan Pendidik'},
            ],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_akuntansi(request):
    """View for profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-akuntansi',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_akuntansi()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('akuntansi')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'akuntansi'
    }
    
    return render(request, 'pages/prodi.html', context)

# Hospitality & Pariwisata
def create_default_profile_page_hospitality():
    """Create default profile page with standardized content blocks for Hospitality"""
    try:
        prodi = ProgramStudi.objects.get(slug='hospitality')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="Hospitality & Tourism",
        slug="prodi-hospar",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi Hospitality & Tourism Matana University',
            'meta_keywords': 'hospitality matana, tourism matana'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 HOSPITALITI & PARIWISATA',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi Hospitaliti dan Pariwisata',
            'description': 'Program Studi Hospitaliti dan Pariwisata Matana University dirancang bagi mahasiswa untuk mengembangkan pemahaman dan keterampilan mendasar pada bidang-bidang utama dari aspek manajemen dan operasional di industri Hospitaliti dan Pariwisata. Dengan bergabung dalam program ini, mahasiswa akan diperkenalkan dengan jenis dan keunikan bisnis Hospitaliti dan Pariwisata serta mendapatkan keterampilan manajerial dan operasional yang dibutuhkan dalam bisnis penginapan, restoran, serta dalam sebuah event. Mahasiswa program Hospitaliti dan Pariwisata berkesempatan magang di jajaran mitra bisnis hotel Matana University yang tergabung di Parador Hotel & Resort dan mitra perusahaan bidang Hospitaliti dan Pariwisata lainnya di Tangerang, Jakarta, dan Bali. Mahasiswa program Hospitaliti dan Pariwisata Matana University telah meraih prestasi di lebih dari 30 kompetisi bidang sejenis se-Indonesia.',
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/informatika.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Program studi Hospitaliti dan Pariwisata Menjadi Program Studi Hospitaliti dan Pariwisata yang diakui unggul dalam bidang hotel management, event management, food production management, dan pariwisata yang berwawasan nasional dan internasional, serta berjiwa entrepreneur untuk meningkatkan kualitas ilmu dan pengetahuan yang merupakan Karunia Tuhan untuk kesejahteraan umat manusia dengan berorientasi pada industri.'
                },
                {
                    'title': 'Misi',
                    'description': 'Terbentuknya sarjana Hospitaliti dan Pariwisata dalam bidang hotel management, event management, food production management, dan pariwisata yang kompeten dan memiliki jiwa entrepreneur, kepemimpinan, serta berperilaku sesuai dengan normanorma di masyarakat, bertanggung jawab dengan layanan penuh kasih.'
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': 'Mendidik dan mempersiapkan lulusan program studi hospitaliti dan pariwisata yang penuh kasih, berintegritas, profesional, dan ahli di bidangnya, berjiwa enterpreneur dan mampu bersaing dan berkiprah dalam dunia bisnis nasional dan internasional. Melaksanakan penelitian dan pengabdian kepada masyarakat melalui publikasi untuk kemajuan ilmu pengetahuan di bidang hotel management, event management, food production management, dan pariwisata dalam memajukan kualitas kehidupan sebagai bentuk kepedulian dalam masyarakat yang berkelanjutan.',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'Culinary Arts'},
                {'title': 'Hotel Management'},
                {'title': 'Mice & Tourism'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {'title': 'Front Office Operation'},
                {'title': 'Housekeeping Operation'},
                {'title': 'Basic English for Room Division Operation'},
                {'title': 'Restaurant Operations'},
                {'title': 'Beverage Service'},
                {'title': 'Food Production'},
                {'title': 'Bakery & Pastry'},
                {'title': 'Event Management'},
                {'title': 'Basic English for Food and Beverage Operation'},
                {'title': 'Business English for Hospitality'},
                {'title': 'Research Methodology'},
                {'title': 'Seni Kuliner'},
                {'title': 'Tourism Economy'},
                {'title': 'Eco Tourism'},
                {'title': 'Hotel Asset management'},
                {'title': 'Managing Festival & Special Event'},
                {'title': 'Consumer Behaviour'},
                {'title': 'Supervisory'},
            ],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {'title': 'Chef'},
                {'title': 'Hotel & Restaurant Operation Management'},
                {'title': 'Event Organizer Management'},
                {'title': 'Entrepreneur'},
                {'title': 'Lecturer'},
                {'title': 'Airlines Crew'},
            ],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_hospitality(request):
    """View for Hospitality & Tourism profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-hospar',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_hospitality()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('hospar')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'hospar'
    }
    
    return render(request, 'pages/prodi.html', context)

# Prodi FSKOM
# Fisika Medis
def create_default_profile_page_fisika_medis():
    """Create default profile page with standardized content blocks for Fisika Medis"""
    try:
        prodi = ProgramStudi.objects.get(slug='fisika_medis')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="S1 FISIKA MEDIS",
        slug="prodi-fisika-medis",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi S1 Fisika Medis Matana University - Unggul dalam bidang fisika dan aplikasinya untuk sektor medis',
            'meta_keywords': 'fisika medis, matana university, radiodiagnostik, radioterapi, kedokteran nuklir'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 FISIKA MEDIS',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi Fisika Medis',
            'description': 'Program S1 Fisika Matana University memiliki konsentrasi Fisika Medis yang mempersiapkan para lulusan untuk menjadi Fisikawan Medik, yaitu tenaga kesehatan profesional yang dilindungi oleh undang-undang untuk mempraktikkan ilmu Fisika Medis. Fisikawan medik bekerja di institusi fasilitas pelayanan kesehatan, akademik, penelitian, dan perusahaan di bidang medis sebagai penguji alat kesehatan. Kurikulum yang digunakan di prodi S1 Fisika Matana University telah mengikuti standar yang ditetapkan oleh Himpunan Fisika Indonesia (HFI) dan Aliansi Institusi Pendidikan Fisika Medis Indonesia (AIPFMI).',
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/informatika.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Menjadi program studi yang terpercaya dan terkemuka dalam bidang fisika dan aplikasinya untuk sektor medis yang berwawasan nasional dan internasional serta berperan dalam peningkatan kualitas iman kepercayaan, ilmu pengetahuan dan teknologi yang merupakan karunia Tuhan, untuk kecerdasan dan kesejahteraan umat manusia serta kehidupan yang lebih baik dan berkelanjutan.'
                },
                {
                    'title': 'Misi',
                    'description': '1. Membentuk lulusan yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih.\n2. Membentuk lulusan yang memiliki kemampuan meneliti, kreatif, dan inovatif dalam bidang fisika dan aplikasinya untuk sektor medis serta berjiwa wirausaha.\n3. Membentuk lulusan yang memiliki kepedulian untuk kehidupan berkelanjutan.'
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'Fisika Medis'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {'title': 'Fisika Klasik'},
                {'title': 'Fisika Modern'},
                {'title': 'Fisika Radiologi'},
                {'title': 'Dosimetri'},
                {'title': 'Radioterapi'},
                {'title': 'Pencitraan Medis'},
                {'title': 'Anatomi dan Fisiologi'},
                {'title': 'Fisika Nuklir'},
                {'title': 'Proteksi Radiasi'},
            ],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {'title': 'Badan Riset dan Inovasi Nasional (BRIN)'},
                {'title': 'Badan Pengkajian dan Penerapan Teknologi (BPPT)'},
                {'title': 'Badan Pengawas Tenaga Nuklir'},
                {'title': 'Peneliti'},
                {'title': 'Fisikawan Medik di Rumah Sakit'},
                {'title': 'Petugas Proteksi Radiasi'},
                {'title': 'Lembaga Ilmu Pengetahuan Indonesia (LIPI)'},
            ],
            'order': 7
        },
    ]
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_fisika_medis(request):
    """View for Fisika Medis profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-fisika-medis',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_fisika_medis()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('fisika-medis')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'fisika-medis'
    }
    
    return render(request, 'pages/prodi.html', context)

# Teknik Informatika
def create_default_profile_page_teknik_informatika():
    """Create default profile page with standardized content blocks for Teknik Informatika"""
    try:
        prodi = ProgramStudi.objects.get(slug='informatika')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="S1 TEKNIK INFORMATIKA",
        slug="prodi-teknik-informatika",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi Teknik Informatika Matana University',
            'meta_keywords': 'teknik informatika matana'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 TEKNIK INFORMATIKA',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi Teknik Informatika',
            'description': 'Program Studi Teknik Informatika Matana University berfokus untuk menghasilkan lulusan yang mampu mengimplementasikan algoritma pada aplikasi yang dirancangbangun baik berbasis web, mobile maupun desktop dengan memanfaatkan basis data dan menambahkan fitur Artificial Intelligence. Dengan Sertifikasi Internasional (MTCNA/Android/Microsoft) dan Sertifikasi Nasional (BNSP), para mahasiswa Teknik Informatika Matana University berkesempatan menjalani program magang dan penyaluran kerja dengan perusahaan-perusahaan IT yang telah bermitra dengan Matana University.',
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/informatika.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': '"Menjadi Program Studi Teknik Informatika yang terpercaya dan terkemuka dalam bidang Human Computer Interaction, dan Graphics and Visual Computing pada sektor kesehatan di provinsi Banten pada tahun 2032" or Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
                },
                {
                    'title': 'Misi',
                    'description': 'Membentuk lulusan yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih. Membentuk lulusan yang memiliki kemampuan meneliti, kreatif, dan inovatif dalam bidang sains data untuk sektor kesehatan serta berjiwa wirausaha. Membentuk lulusan yang memiliki kepedulian untuk kehidupan berkelanjutan.' or 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': 'Terbentuknya lulusan yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih. Terbentuknya lulusan yang memiliki kemampuan meneliti, kreatif, dan inovatif dalam bidang komputer sains untuk sektor kesehatan yang berjiwa kewirausahaan. Terbentuknya lulusan yang memiliki kepedulian untuk kehidupan berkelanjutan..',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'Artificial Intelligence Engineering'},
                {'title': 'Digital Entrepreneurship'},
                {'title': 'Software Engineering'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {'title': 'Artificial Intelligence'},
                {'title': 'Database System'},
                {'title': 'Computer Science'},
                {'title': 'Software Engineering'},
                {'title': 'Computer Systems and Networks'},
                {'title': 'Computer Security'},
                {'title': 'Human-Computer Interaction'},
                {'title': 'Information Management and Analytics'},
                {'title': 'Game Development'},
            ],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {'title': 'Front End Developer (UI/UX)'},
                {'title': 'Back End Developer'},
                {'title': 'Full Stack Developer (Front End & Back End)'},
                {'title': 'Software Engineer'},
                {'title': 'Technology Support'},
                {'title': 'System Analyst'},
                {'title': 'Network Engineer'},
                {'title': 'Data Scientist'},
                {'title': 'Artificial Intelligence Specialist'},
                {'title': 'Mobile apps developer'},
                {'title': 'Game Developer'},
            ],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

# @togglable_cache()
# def profile_view_teknik_informatika(request):
#     """View for Teknik Informatika profile page"""
#     try:
#         profile_page = Page.objects.get(
#             slug='prodi-teknik-informatika',
#             status=Page.PUBLISHED
#         )
#     except Page.DoesNotExist:
#         profile_page = create_default_profile_page_teknik_informatika()
    
#     # Get content blocks
#     blocks = {}
#     for block in profile_page.content_blocks.all().order_by('order'):
#         blocks[block.identifier] = block.content

#     # Get related articles
#     related_articles = get_related_articles('informatika')
    
#     context = {
#         'page': profile_page,
#         'meta': profile_page.metadata,
#         'blocks': blocks,
#         'blocks_popup': {
#             i.identifier: i.content 
#             for i in Page.objects.get(
#                 slug='popup', 
#                 status=Page.PUBLISHED
#             ).content_blocks.all().order_by('order')
#         },
#         'related_articles': related_articles,
#         'prodi_category': 'informatika'
#     }
    
#     return render(request, 'pages/prodi.html', context)

# Teknik Informatika
def create_default_profile_page_statistika():
    """Create default profile page with standardized content blocks for Statistika (Data Science)"""
    try:
        prodi = ProgramStudi.objects.get(slug='statistika')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="S1 STATISTIKA (DATA SCIENCE)",
        slug="prodi-statistika",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi Statistika Matana University - Unggul dalam bidang Sains Data untuk sektor kesehatan, sosial, bisnis, dan finansial',
            'meta_keywords': 'statistika, matana university, sains data, aktuaria, machine learning'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 STATISTIKA (DATA SCIENCE)',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi Statistika',
            'description': 'Program studi Statistika Universitas Matana adalah salah satu jurusan yang paling dibutuhkan di Era Digital (Big Data) seperti sekarang ini. Mahasiswa/i dibekali dengan kemampuan analisis data yang mempuni untuk dapat diterapkan dalam bidang bisnis, aktuaria dan sains data.',
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/hospar.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': '"Menjadi program studi yang terpercaya dan terkemuka dalam bidang sains data untuk sektor kesehatan, sosial, bisnis dan finansial, yang berwawasan nasional dan internasional serta berperan dalam peningkatan kualitas iman kepercayaan, ilmu pengetahuan dan teknologi yang merupakan karunia Tuhan untuk kecerdasan dan kesejahteraan umat manusia serta kehidupan yang lebih baik dan berkelanjutan"'
                },
                {
                    'title': 'Misi',
                    'description': 'Membentuk lulusan yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih. Membentuk lulusan yang memiliki kemampuan meneliti, kreatif, dan inovatif dalam bidang sains data untuk sektor kesehatan, sosial, bisnis dan finansial serta berjiwa wirausaha. Membentuk lulusan yang memiliki kepedulian untuk kehidupan berkelanjutan.'
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'Sains Data'},
                {'title': 'Aktuaria'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {'title': 'Akuntansi'},
                {'title': 'Ekonomi'},
                {'title': 'Ekonometrika'},
                {'title': 'Manajemen Resiko'},
                {'title': 'Manajemen Aktuaria'},
                {'title': 'Matematika Keuangan'},
                {'title': 'Matematika Asuransi'},
                {'title': 'Sains Data'},
                {'title': 'Komputasi Statistika'},
                {'title': 'Modern Prediction & Machine Learning'},
            ],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {'title': 'Pendidik'},
                {'title': 'PNS'},
                {'title': 'Peneliti'},
                {'title': 'Data Analyst'},
                {'title': 'Data Scientist'},
                {'title': 'Aktuaris'},
                {'title': 'Electronic Data Processing'},
                {'title': 'Konsultan Data'},
                {'title': 'Investasi dan Dana Pensiun'},
                {'title': 'Perbankan'},
                {'title': 'Konsultan Aktuaria'},
            ],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_informatika(request):
    """View for Teknik Informatika profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-teknik-informatika',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_teknik_informatika()
    
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('informatika')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'informatika'
    }
    
    return render(request, 'pages/prodi.html', context)


@togglable_cache()
def profile_view_statistika(request):
    """View for Statistika profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-statistika',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_statistika()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('statistika')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'statistika'
    }
    
    return render(request, 'pages/prodi.html', context)

# Prodi FSDH
# DKV
def create_default_profile_page_dkv():
    """Create default profile page with standardized content blocks for Desain Komunikasi Visual"""
    try:
        prodi = ProgramStudi.objects.get(slug='dkv')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="S1 DESAIN KOMUNIKASI VISUAL",
        slug="prodi-dkv",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi Desain Komunikasi Visual Universitas Matana - Mengusung integritas kurikulum yang menyeimbangkan teknik tradisional dan digital',
            'meta_keywords': 'desain komunikasi visual, matana university, desain grafis, ilustrasi, fotografi, videografi'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 DESAIN KOMUNIKASI VISUAL',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi Desain Komunikasi Visual',
            'description': 'Program Studi Desain Komunikasi Visual Universitas Matana mendorong agar lulusannya mampu bekerja dengan baik di ranah profesi yang sudah ada, serta mampu menciptakan peluang dan inovasi dalam bidang Seni Rupa dan Desain.',
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/hospar.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Menjadi program studi yang terpercaya dan terkemuka dalam menumbuhkembangkan karakter intelektual seni rupa dan desain yang mandiri, yang senantiasa mengedepankan wawasan keindonesiaan di kancah global, demi berlangsungnya tatanan peradaban, yang merupakan karunia Tuhan untuk kemanusiaan.'
                },
                {
                    'title': 'Misi',
                    'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'Desain Grafis'},
                {'title': 'Ilustrasi'},
                {'title': 'Fotografi & Videografi'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [
                {'title': 'Design Basics'},
                {'title': 'Lettering & Type'},
                {'title': 'History of Art & Design'},
                {'title': 'Drawing'},
                {'title': 'Digital Media Communication'},
                {'title': 'Creative Art Methodology'},
                {'title': 'Visual Thinking & Perception'},
                {'title': 'Photography & Videography'},
                {'title': 'Contextual Design'},
            ],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [
                {'title': 'Graphic Designer'},
                {'title': 'Web Designer'},
                {'title': 'Packaging Designer'},
                {'title': 'Brand Consultant'},
                {'title': 'UI/UX Designer'},
                {'title': 'Visual Identity Designer'},
                {'title': 'Illustrator'},
                {'title': 'Character Designer'},
                {'title': 'Art Curator'},
                {'title': 'Art Journalist / Critics'},
                {'title': 'Art Director'},
                {'title': 'Creative Director'},
                {'title': 'Photographer'},
                {'title': 'Videographer'},
                {'title': 'Content Creator'},
            ],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_dkv(request):
    """View for Desain Komunikasi Visual profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-dkv',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_dkv()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('dkv')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'dkv'
    }
    
    return render(request, 'pages/prodi.html', context)

# Arsitektur
def create_default_profile_page_arsitektur():
    """Create default profile page with standardized content blocks for Arsitektur"""
    try:
        prodi = ProgramStudi.objects.get(slug='arsitektur')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="S1 ARSITEKTUR",
        slug="prodi-arsitektur",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi Arsitektur Matana University',
            'meta_keywords': 'arsitektur matana'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 ARSITEKTUR',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi Arsitektur',
            'description': "Program S1 Arsitektur Matana University didesain untuk menghasilkan lulusan dengan paradigma 'think globally, act locally', dimana mahasiswa dibekali konsep global dalam merancang bangunan, permukiman dan sebuah kawasan dengan pendekatan desain cerdas (smart), yang berbasis Green, TOD (Transit Oriented Development) dan Teknologi (industri 5.0), namun begitu, dalam eksekusinya tetap berpijak pada konteks (iklim, budaya, estetika, sejarah, hukum, etika, dll) dan lokalitas yang melingkupinya.",
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/hospar.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': "Menjadi Program Studi Arsitektur yang terkemuka dalam akademik dan profesionalisme yang berwawasan Nasional serta Internasional, yang berperan dalam peningkatan kualitas iman kepercayaan, ilmu pengetahuan dan teknologi, untuk kecerdasan dan kesejahteraan umat manusia serta lingkungan binaan yang berkelanjutan"
                },
                {
                    'title': 'Misi',
                    'description': "Menghasilkan lulusan yang memiliki jiwa kepemimpinan serta berdedikasi pada perilaku etis, bertanggung jawab berlandaskan layanan penuh kasih.\nMenghasilkan lulusan yang memiliki kompetensi di bidang perencanaan, perancangan dan penelitian, serta kreatif, inovatif dan memiliki jiwa kewirausahaan.\nMenghasilkan generasi penerus yang memiliki kepedulian untuk kehidupan berkelanjutan."
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': "a.\tMendidik dan mempersiapkan lulusan yang penuh kasih, berintegritas. profesional, inovatif dan ahli di bidang perencanaan & perancangan Arsitektur, berjiwa kewiraushaan yang mampu bersaing dan berkiprah dalam dunia bisnis nasional serta internasional.\nb.\tMelaksanakan penelitian dan upaya lainnya untuk kemajuan ilmu pengetahuan, teknologi,  kesenian dan kebudayaan yang terkait dengan Arsitektur yang dapat memajukan kualitas kehidupan masyarakat.\nc.\tMelaksanakan Pengabdian Kepada Masyarakat (PKM) sebagai bentuk aktualisasi ilmu dan pengetahuan di tengah-tengahmasyarakat.",
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'Perancangan Arsitektur Bangunan'},
                {'title': 'Perancangan Pemukiman dan Kawasan'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [{"title": "Studio Perancangan Arsitektur"}, {"title": "Studio Struktur & Konstruksi"}, {"title": "Komputasi dalam Arsitektur"}, {"title": "Manajemen Konstruksi"}, {"title": "Studio Perancangan Pemukiman"}, {"title": "Studio Perancangan Kawasan"}, {"title": "Pengembangan Kawasan"}, {"title": "Metode Perencanaan dan Perancangan"}],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [{"title": "Arsitek Konsultan Arsitektur"}, {"title": "Konsultan Manajemen Konstruksi"}, {"title": "Perencana Konsultan Kawasan & Kota"}],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

# Arsitektur
def create_default_popup():
    """Create default profile page with standardized content blocks for Arsitektur"""
    try:
        prodi = ProgramStudi.objects.get(slug='admin')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="POPUP",
        slug="popup",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi Arsitektur Matana University',
            'meta_keywords': 'arsitektur matana',
            'is_active': True  # Add flag to control popup visibility
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'POPUP',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1
        },
        {
            'identifier': 'description_section',
            'title': 'Penerimaan Mahasiswa Baru 2025',
            'description': 'Wujudkan impianmu menjadi bagian dari Matana University. Dapatkan kesempatan beasiswa hingga 100% dan fasilitas pembelajaran berkualitas internasional.',
            'order': 2
        },
        {
            'identifier': 'button_section',
            'title': 'Pendaftaran',
            'items': [
                {
                    'title': 'Daftar Sekarang',
                    'description': 'https://pmb.matanauniversity.ac.id/'
                },
                {
                    'title': 'Info Beasiswa',
                    'description': '/beasiswa/'
                }
            ],
            'order': 3
        },
     
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page


@togglable_cache()
def profile_view_arsitektur(request):
    """View for Arsitektur profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-arsitektur',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_arsitektur()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('arsitektur')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'arsitektur'
    }
    
    return render(request, 'pages/prodi.html', context)

# Prodi FKK

# K3
def create_default_profile_page_k3():
    """Create default profile page with standardized content blocks for K3"""
    try:
        prodi = ProgramStudi.objects.get(slug='k3')
    except ProgramStudi.DoesNotExist:
        return None
        
    profile_page = Page.objects.create(
        title="S1 Keselamatan & Kesehatan Kerja(K3)",
        slug="prodi-k3",
        template='prodi.html',
        status=Page.PUBLISHED,
        program_studi=prodi,
        metadata={
            'meta_description': 'Program Studi K3 Matana University - Program S1 K3 dengan paradigma think globally, act locally',
            'meta_keywords': 'k3 matana, kesehatan kerja, keselamatan kerja'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'S1 Keselamatan & Kesehatan Kerja(K3)',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1,
            'items': [
                {
                    'title': 'Akreditasi',
                    'description': 'B'
                },
                {
                    'title': 'Lama Studi',
                    'description': '4 Tahun'
                },
                {
                    'title': 'Bahasa',
                    'description': 'ID/EN'
                },
            ]
        },
        {
            'identifier': 'description_section',
            'title': 'Program Studi K3',
            'description': 'Program Studi K3 mempelajari cara pencegahan dan pengelolaan risiko kecelakaan kerja dan penyakit akibat kelalaian; demi meningkatkan motivasi dan efisiensi produktivitas kerja, serta terciptanya lingkungan kerja yang sehat dan aman. Program studi ini memiliki dosen akademisi dan praktisi berpengalaman di bidang K3, serta sarana laboratorium yang lengkap untuk menghasilkan lulusan K3 (dengan gelar S.KKK) yang kompeten dan mumpuni sesuai kebutuhan diberbagai industri antara lain manufaktur, konstruksi, pertambangan, minyak dan gas bumi, serta bidang kesehatan.',
            'order': 2
        },
        {
            'identifier': 'visi_misi_section',
            'background_image': '/static/images/hospar.jpg',
            'title': 'Visi & Misi',
            'items': [
                {
                    'title': 'Visi',
                    'description': 'Menjadi program studi terkemuka yang menghasilkan sarjana profesional di bidang K3 (S. Kes) dengan keahlian dalam kesehatan, keselamatan kerja, ergonomi, human factor, dan higiene industri yang berwawasan nasional dan internasional dalam ilmu pengetahuan dan teknologi untuk mendukung kecerdasan dan kesejahteraan umat manusia, serta mewujudkan kehidupan yang lebih baik dan berkelanjutan.'
                },
                {
                    'title': 'Misi',
                    'description': "Menyelenggarakan pendidikan untuk menghasilkan lulusan Keselamatan dan Kesehatan Kerja (K3) yang memiliki jiwa kepemimpinan yang kuat, berdedikasi pada perilaku etis, bertanggung jawab, dan berlandaskan pada layanan yang penuh kasih;\nMelaksanakan kegiatan penelitian untuk menghasilkan lulusan Keselamatan dan Kesehatan Kerja (K3) yang unggul dalam kemampuan penelitian, kreativitas, inovasi, dan berjiwa kewirausahaan;\nMenyelenggarakan kegiatan pengabdian kepada masyarakat untuk menghasilkan lulusan Keselamatan dan Kesehatan Kerja (K3) yang memiliki kepedulian tinggi terhadap kehidupan berkelanjutan."
                }
            ],
            'order': 3
        },
        {
            'identifier': 'tujuan_section',
            'title': 'Tujuan',
            'description': "1.\tMendidik dan mempersiapkan lulusan program studi K3 yang penuh kasih, berintegritas, profesional, inovatif dan ahli di bidangnya, berjiwa Entrepreneur dan mampu bersaing dan berkiprah dalam dunia bisnis nasional dan internasional.\n\n2.\tMelaksanakan penelitian dan implementasi keilmuan K3 melalui publikasi untuk operasional dan kewirausahaan dalam memajukan kualitas kehidupan masyarakat.\n\n3.\tMelaksanakan pengabdian kepada masyarakat sesui kebutuhan sebagai aktualisasi penerapan ilmu keselamatan dan kesehatan kerja, operasional dan kewirausahaan sebagai bentuk kepedulian atas kehidupan masyarakat yang berkelanjutan",
            'order': 4
        },
        {
            'identifier': 'konsentrasi_section',
            'title': 'Konsentrasi',
            'items': [
                {'title': 'General Occupational Health and Safety (Ahli K3 umum)'},
            ],
            'order': 5
        },
        {
            'identifier': 'kurikulum_section',
            'title': 'Kurikulum',
            'items': [{"title": "Pengantar Ilmu Kesehatan Masyarakat"}, {"title": "Ilmu Biomedik Dasar"}, {"title": "Fisika dan Kimia dalam K3"}, {"title": "Fisiologi Kerja"}, {"title": "Dasar Keselamatan dan Kesehatan Kerja"}, {"title": "Komunikasi & Promosi"}, {"title": "Biostatistik"}, {"title": "Prinsip Keselamatan Kerja"}, {"title": "Pengantar Higiene Industri"}, {"title": "Pengantar Kesehatan Lingkungan"}, {"title": "Peraturan Perundangan K3"}, {"title": "Gizi Kerja"}, {"title": "Epidemiologi"}, {"title": "Prinsip Kesehatan Kerja"}, {"title": "Ergonomi"}, {"title": "Aspek Manusia Dalam K3"}, {"title": "Psikososial di Tempat Kerja"}, {"title": "Manajemen Bising Getar"}, {"title": "Manajemen B3"}, {"title": "Bahaya Kimia & Biomonitoring"}],
            'order': 6
        },
        {
            'identifier': 'peluang_karir_section',
            'title': 'Peluang Karir',
            'items': [{"title": "Environmental Specialist"}, {"title": "Analist Quality Control"}, {"title": "Health and Safety Engineer"}, {"title": "Pengawas Konstruksi Bangunan"}, {"title": "Advisor dan Auditor K3"}, {"title": "Ahli Ergonomi"}, {"title": "Ahli K3 Rumah Sakit"}, {"title": "Corporate Safety"}, {"title": "Spesialis Kebakaran"}, {"title": "Industrial Hygiene"}, {"title": "Permit to Work Coordinator"}],
            'order': 7
        },
    ]
    
    create_standardized_blocks(profile_page, default_blocks)
    return profile_page

@togglable_cache()
def profile_view_k3(request):
    """View for Arsitektur profile page"""
    try:
        profile_page = Page.objects.get(
            slug='prodi-k3',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        profile_page = create_default_profile_page_k3()
    
    # Get content blocks
    blocks = {}
    for block in profile_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content

    # Get related articles
    related_articles = get_related_articles('k3')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'k3'
    }
    
    return render(request, 'pages/prodi.html', context)

@togglable_cache()
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

    # Get related articles
    related_articles = get_related_articles('profil-matana')
    
    context = {
        'page': profile_page,
        'meta': profile_page.metadata,
        'blocks': blocks,
        'blocks_popup': {
            i.identifier: i.content 
            for i in Page.objects.get(
                slug='popup', 
                status=Page.PUBLISHED
            ).content_blocks.all().order_by('order')
        },
        'related_articles': related_articles,
        'prodi_category': 'profil-matana'
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
    # Check if user is superuser or has article program studi permission
    is_article_admin = False
    if not request.user.is_superuser:
        try:
            prodi_admin = ProdiAdmin.objects.get(user=request.user)
            is_article_admin = prodi_admin.program_studi.filter(slug='article').exists()
        except ProdiAdmin.DoesNotExist:
            return render(request, 'admin/article_list.html', {
                'articles': [],
                'categories': [],
                'total_articles': 0,
                'published_count': 0,
                'draft_count': 0,
                'featured_count': 0,
                'recent_articles': []
            })

    if not (request.user.is_superuser or is_article_admin):
        return render(request, 'admin/article_list.html', {
            'articles': [],
            'categories': [],
            'total_articles': 0,
            'published_count': 0,
            'draft_count': 0,
            'featured_count': 0,
            'recent_articles': []
        })

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
                    'icon': 'fa-clipboard'
                },
                {
                    'title': 'Upload Dokumen',
                    'description': 'Upload dokumen yang diperlukan (Ijazah, Transkrip, dll)',
                    'icon': 'fa-upload'
                },
                {
                    'title': 'Pembayaran Registrasi',
                    'description': 'Lakukan pembayaran biaya pendaftaran',
                    'icon': 'fa-receipt'
                },
                {
                    'title': 'Tes Masuk',
                    'description': 'Ikuti tes potensi akademik dan wawancara',
                    'icon': 'fa-pen'
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
        'blocks': blocks, 'blocks_popup': { i.identifier: i.content for i in Page.objects.get(slug='popup', status=Page.PUBLISHED).content_blocks.all().order_by('order')  }  # Simplified - just send all blocks
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
                # {
                #     'text': 'Lihat Program Beasiswa',
                #     'url': '#scholarship-programs',
                #     'style': 'primary'
                # },
                {
                    'text': 'Daftar Sekarang',
                    'url': 'https://matanauniversity.siakadcloud.com/spmbfront/',
                    'style': 'secondary'
                }
            ],
            'order': 1
        },
        {
            'identifier': 'scholarship_programs1',
            'title': 'GELOMBANG 2 TAHUN AKADEMIK 2025/2026',
            'description': 'Program Beasiswa untuk mahasiswa yang memiliki potensi dan kemampuan untuk menjadi pemimpin masa depan.',
            'items': [
               {    
                'title': 'Benefit',
               },
               {
                'description': 'Potongan Uang Gedung 90%\nKuliah 8 Semester, Bayar 7 Semester (GRATIS 1 Semester)\nPotongan Uang Kuliah hingga 70% selama 7 Semester',
               },
               {
                'title': 'Persyaratan',
               },
               {
                'description': 'Melampirkan fotokopi rapor kelas 10 dan 11\nBerlaku untuk pendaftaran kuliah Agustus 2025',
               }
            ],
            'order': 2
        },
        {
            'identifier': 'scholarship_programs2',
            'title': 'BEASISWA FUTURE LEADER',
            'description': 'Program Beasiswa untuk mahasiswa yang memiliki potensi dan kemampuan untuk menjadi pemimpin masa depan.',
            'items': [
                {
                        'title': 'Benefit',
                },
                {
                    'description': 'Pendaftaran kuliah bersama 3-5 orang\nCashback berupa potongan uang kuliah semester 2\nMelampirkan fotokopi rapor kelas 10 dan 11',
                },
                {
                    'title': 'Persyaratan',
                },
                {
                    'description': 'Merupakan leader/anggota dari komunitas (OSIS, keagamaan, atau komunitas lainnya)\nMelampirkan surat rekomendasi dari sekolah/komunitas',
                }
                ],
            'order': 3  
        },
        {
            'identifier': 'scholarship_programs3',
            'title': 'BEASISWA INFLUENCER',
            'description': 'Program Beasiswa untuk mahasiswa yang memiliki potensi dan kemampuan untuk menjadi pemimpin masa depan.',
            'items': [
                {
                    'title': 'Benefit',
                },
                {
                    'description': 'Bebas Uang Gedung 100%\nKuliah 8 Semester, Bayar 7 Semester (Semester 8 GRATIS)\nPotongan Uang Kuliah 50% selama 7 Semester',
                },
                {
                    'title': 'Persyaratan',
                },
                {
                    'description': 'Merupakan leader/anggota dari komunitas (OSIS, keagamaan, atau komunitas lainnya)\nMelampirkan surat rekomendasi dari sekolah/komunitas',
                }
            ],
            'order': 4
        },
        {
            'identifier': 'scholarship_programs4',
            'title': 'BEASISWA ATLET',
            'description': 'Program Beasiswa untuk mahasiswa yang memiliki potensi dan kemampuan untuk menjadi pemimpin masa depan.',
            'items': [
                {
                    'title': 'Benefit',
                },
                {
                    'description': 'Potongan Uang Gedung 90%\nKuliah 8 Semester, Bayar 7 Semester (Semester 8 GRATIS)\nPotongan Uang Kuliah 50%-80% selama 7 Semester',
                },
                {
                    'title': 'Persyaratan',
                },
                {
                    'description': 'Aktif dalam perlombaan dan UKM yang akan dipantau oleh Departemen Kemahasiswaan\nMemenuhi syarat dan ketentuan yang ditetapkan oleh Departemen Kemahasiswaan',
                }
            ],
            'order': 5
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
        beasiswa_page = []
        for block in scholarship_page.content_blocks.all().order_by('order'):
            try:
                blocks[block.identifier] = block.content
                if 'scholarship_programs' in block.identifier:
                    beasiswa_page.append(block.content)
            except Exception as e:
                print(f"Error processing block {block.identifier}: {str(e)}")
                continue
        
        context = {
            'page': scholarship_page,
            'meta': scholarship_page.metadata,
            'blocks': blocks, 'blocks_popup': { i.identifier: i.content for i in Page.objects.get(slug='popup', status=Page.PUBLISHED).content_blocks.all().order_by('order')  },
            'beasiswa_page': beasiswa_page,
        }
        
        
    except Exception as e:
        print(f"Error rendering scholarship page: {str(e)}")
        raise Http404("Page could not be rendered")
    return render(request, 'pages/scholarship.html', context)

@login_required
def article_save(request):
    try:
        with transaction.atomic():
            article_id = request.POST.get('article_id')
            article = Article.objects.get(id=article_id) if article_id else Article()
            
            # Check permissions
            if article_id and not article.can_edit(request.user):
                messages.error(request, 'You do not have permission to edit this article')
                return redirect('article_list')

            # Validate required fields
            required_fields = ['title', 'excerpt', 'content', 'category']
            for field in required_fields:
                if not request.POST.get(field):
                    messages.error(request, f'{field.title()} is required')
                    return redirect('article_edit', pk=article_id) if article_id else redirect('article_create')

            # Update article fields
            article.title = request.POST.get('title')
            article.featured_image = request.POST.get('featured_image')
            article.excerpt = request.POST.get('excerpt')
            article.content = request.POST.get('content')
            article.category_id = request.POST.get('category')
            article.meta_description = request.POST.get('meta_description', '')
            article.meta_keywords = request.POST.get('meta_keywords', '')
            article.is_featured = request.POST.get('is_featured') == 'on'

            # Handle status changes
            old_status = article.status if article_id else None
            new_status = request.POST.get('status')

            # Handle resubmission of rejected article
            if request.POST.get('resubmit') and article.status == 'rejected':
                if request.user != article.created_by:
                    messages.error(request, 'Only the article creator can resubmit a rejected article')
                    return redirect('article_edit', pk=article_id)
                new_status = 'pending'
                article.review_comment = None
                article.reviewed_by = None
                article.reviewed_at = None

            # Handle status changes by superuser
            elif request.user.is_superuser and article.status != 'published':
                if new_status in ['published', 'rejected', 'on_review']:
                    article.status = new_status
                    article.reviewed_by = request.user
                    article.reviewed_at = timezone.now()
                    article.review_comment = request.POST.get('review_comment', '')
            else:
                # Non-superusers can only submit/resubmit
                if not article_id or article.status == 'rejected':
                    article.status = 'pending'
                    article.review_comment = None
                    article.reviewed_by = None
                    article.reviewed_at = None

            if not article_id:
                article.created_by = request.user
            article.updated_by = request.user

            # Generate slug if needed
            if not article.slug:
                article.slug = slugify(article.title)

            article.save(update_fields=['title', 'status', 'featured_image', 'excerpt', 'content', 
                                       'category_id', 'meta_description', 'meta_keywords', 
                                       'is_featured', 'published_at'])

            # Create review history if status changed
            if old_status != article.status:
                ArticleReviewHistory.objects.create(
                    article=article,
                    status=article.status,
                    comment=article.review_comment,
                    reviewed_by=request.user
                )

            messages.success(request, 'Article saved successfully!')
            return redirect('article_edit', pk=article.id)

    except Exception as e:
        logger.error(f"Error saving article: {str(e)}")
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

@login_required
def page_list_view(request):
    """View for listing all pages"""
    if request.user.is_superuser:
        pages = Page.objects.all()
    elif request.user.groups.filter(name='prodi_admin').exists():
        try:
            prodi_admin = ProdiAdmin.objects.get(user=request.user)
            if prodi_admin.is_active:
                # Get all pages for all program studi managed by this admin
                pages = Page.objects.filter(program_studi__in=prodi_admin.program_studi.all())
            else:
                pages = Page.objects.none()
        except ProdiAdmin.DoesNotExist:
            pages = Page.objects.none()
    else:
        # raise PermissionDenied("You don't have permission to view pages")
        pages = Page.objects.none()

    context = {
        'pages': pages.order_by('-updated_at'),
        'title': 'Pages',
        'subtitle': 'Manage your website pages'
    }
    
    return render(request, 'admin/page_list.html', context)

def create_default_management_page():
    """Create default management page with standardized content blocks"""
    management_page = Page.objects.create(
        title="Manajemen",
        slug="manajemen",
        template='management.html',
        status=Page.PUBLISHED,
        metadata={
            'meta_description': 'Manajemen Matana University - Rektorat dan Dekan',
            'meta_keywords': 'manajemen matana, rektorat matana, dekan matana'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Manajemen Matana University',
            'subtitle': 'Kepemimpinan yang Berdedikasi untuk Pendidikan Berkualitas',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1
        },
        {
            'identifier': 'rektorat_section',
            'title': 'Rektorat & Ketua Lembaga',
            'items': [
                {
                "image": "/static/images/manajemen/r1.jpg",
                "title": "Dr. Melitina Tecolau, S.E, M.M, CFP, CHCP-A",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
                },
                {
                "image": "/static/images/manajemen/r2.jpg",
                "title": "Dr. rer. nat. Gregoria Illya, M.Sc",
                "description": "Dr. rer.nat. Gregoria Illya, peneliti dalam bidang fisika material, fisika komputasi, dan biofisika memperoleh gelar sarjana Fisika dari Universitas Katolik Parahyangan, dan kemudian mendapatkan gelar Master of Engineering Mathematics dari Universitas Twente, Belanda dengan beasiswa dari VNO NCW. Gelar Doktor diperoleh dari Universitas Potsdam Germany dengan disertasi berjudul Bilayer Material Properties From Dissipative Particle Dynamics Simulations yang dilaksanakan pada dan dibiayai penuh oleh Max Planck Institute for Colloids and Interfaces, Jerman.\n\nSetelah menyelesaikan studi doktor, beliau mengambil program Postdoctoral di Max Planck Institute for Polymer Research, Jerman dan menghasilkan publikasi di jurnal internasional bereputasi (Q1) Nature dengan judul: Aggregation and vesiculation of membrane proteins by curvature-mediated interactions. Pada tahun 2006 beliau mendapatkan beasiswa untuk mengikuti program Boulder School for Condensed Matter and Materials Physics di University of Colorado Boulder USA. Program Postdoctoral selanjutnya yang ditempuh oleh beliau adalah di Theoretical Physical Chemistry Department, Technische Universitaet Darmstadt, Jerman dan kemudian di Theoretical Physics Department, Justus-Liebig Universitaet Giessen, Jerman. Beliau pernah menjadi pembicara tamu di International Conference on Materials for Advanced Technologies Singapore pada tahun 2015, 2017 dan 2019 dan pada tahun 2017 beliau terpilih sebagai dosen berprestasi peringkat 1 dari Kopertis IV."
                },
                {
                "image": "/static/images/manajemen/r3.jpg", 
                "title": "Dr. Bernardus Wishman S. Siregar, S.E., M.E.",
                "description": "Dr. Bernardus Wishman S. Siregar, S.E., M.E. adalah seorang profesional yang memiliki pengalaman dalam bidang keuangan dan manajemen. Beliau telah menyelesaikan studi doktor di Universitas Katolik Parahyangan dengan disertasi berjudul \"Analisis Pengaruh Kebijakan Moneter dan Fiskal Terhadap Kinerja Perbankan Syariah di Indonesia\". Beliau juga memiliki pengalaman sebagai dosen di Universitas Katolik Parahyangan dan Universitas Matana, serta sebagai pengajar di Universitas Matana. Beliau juga aktif dalam kegiatan akademik dan penelitian, serta memiliki publikasi di jurnal internasional bereputasi."
                },
                {
                "image": "/static/images/manajemen/r4.jpg",
                "title": "Dr. Lulu Setiawati, S.E., M.Bus., D.Th., CFP, CSA",
                "description": "Dr. Lulu Setiawati, S.E., M.Bus, CFP, CSA telah berkarir di dunia pendidikan di Indonesia sejak 2002. Sebelum berkarir di dunia pendidikan, beliau telah berkarir secara professional di Australia dan Taiwan di berbagai industri. Gelar S.E. diperoleh dari Universitas Kristen Petra dalam bidang Manajemen, selanjutnya beliau mendapatkan gelar M.Bus in Finance dari RMIT, Melbourne.\n\nTahun 2017 beliau mendapatkan gelar Doktor dari Universitas Katolik Widya Mandala dalam bidang Manajemen Stratejik. Tahun 2009 beliau bergabung di UPH Surabaya sebagai dosen Keuangan dan ditunjuk sebagai Ketua Program Studi Akuntansi sejak tahun 2009 hingga tahun 2013.\n\nTahun 2014 selain sebagai dosen, beliau ditunjuk sebagai Manajer Keuangan dan tahun 2015 hingga tahun 2017 beliau juga menjabat sebagai Wakil Rektor bidang keuangan dan administrasi UPH Surabaya. Program pendidikan profesi juga telah beliau tempuh, Beliau telah mendapatkan gelar CFP sebagai perencana keuangan pada tahun 2016 dan pada tahun 2017 beliau mendapatkan gelar CSA sebagai Analis Efek."
                },
                {
                "image": "/static/images/manajemen/r5.jpg",
                "title": "Wijil Nugroho,S.E.,MBA.",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
                },
                {
                "image": "/static/images/manajemen/r6.jpg",
                "title": "Baltasar Serilus Sanggu Dedu., S.Kep., M.Sc",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
                },
                {
                "image": "/static/images/manajemen/r7.jpg",
                "title": "Dr. Kalfin, S.Mat., M.Mat",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
                }
              
            ],
            'order': 2
        },
        {
            'identifier': 'dekan_section',
            'title': 'Dekan & Ketua Program Studi',
     "items": [
    {
      "image": "/static/images/manajemen/d1.jpg",
      "title": "Dr. M. Rachman Mulyandi, s.E, MBA.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d2.jpg",
      "title": "Dr. Ir. Danang Harito Wibowo, M.T., IAI",
      "description": "Dr. Ir. Danang Harito Wibowo, M.T., IAI adalah seorang arsitek profesional yang menyelesaikan pendidikan jenjang S1 – Sarjana Arsitektur (1991) di prodi Arsitektur Universitas Parahyangan, Bandung. Mengikuti Pendidikan lanjut (non gelar – 2011) di Institut Teknologi Bandung. Kemudian menyelesaikan pendidikan jenjang S2 Magister (2012) serta S3 Doktoral (2024) di prodi Arsitektur, Universitas Parahyangan, Bandung. Dengan jam terbang lebih dari 29 tahun sebagai Arsitek profesional, beragam perencanaan dan perancangan bangunan, kawasan dan interior telah dilakukannya (gedung Apartemen, Kantor, Hotel, Café & Resto, Klinik, Hunian dll). Tidak sedikit pula menulis artikel ilmiah hasil penelitian yang telah dilakukan. Menjadikan Dr. Ir. Danang H. Wibowo, M.T., IAI memiliki kualifikasi yang lengkap sebagai Arsitek profesional sekaligus dosen pengajar. Tahun 2009, mulai mengajar sebagai dosen Studio Perancangan Arsitektur 1 – 5 dan beberapa mata kuliah lainnya di Unikom, Bandung. Di tahun 2011 hingga awal 2015, aktif mengajar mata kuliah Studio Perancangan Arsitektur 1 – 6 dan Teknologi Bangunan 1 – 3 di Universitas Pancasila, Jakarta. Di pertengahan tahun 2015 hingga kini, menjadi dosen pengajar tetap (mengajar beberapa mata kuliah utama) dan ketua program studi Arsitektur Universitas Matana."
    },
    {
      "image": "/static/images/manajemen/d3.jpg",
      "title": "PRYA ARTHA WIDJAYA, S.T., M.I.T.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d4.jpg",
      "title": "Ririsma Sihombing, S.E., M.E.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d5.jpg",
      "title": "Yuka Dian Narendra, S.Sn, M.Hum.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d6.jpg",
      "title": "Dr. Ir. Danang Harito Wibowo, M.T., IAI",
      "description": "Dr. Ir. Danang Harito Wibowo, M.T., IAI adalah seorang arsitek profesional yang menyelesaikan pendidikan jenjang S1 – Sarjana Arsitektur (1991) di prodi Arsitektur Universitas Parahyangan, Bandung. Mengikuti Pendidikan lanjut (non gelar – 2011) di Institut Teknologi Bandung. Kemudian menyelesaikan pendidikan jenjang S2 Magister (2012) serta S3 Doktoral (2024) di prodi Arsitektur, Universitas Parahyangan, Bandung. Dengan jam terbang lebih dari 29 tahun sebagai Arsitek profesional, beragam perencanaan dan perancangan bangunan, kawasan dan interior telah dilakukannya (gedung Apartemen, Kantor, Hotel, Café & Resto, Klinik, Hunian dll). Tidak sedikit pula menulis artikel ilmiah hasil penelitian yang telah dilakukan. Menjadikan Dr. Ir. Danang H. Wibowo, M.T., IAI memiliki kualifikasi yang lengkap sebagai Arsitek profesional sekaligus dosen pengajar. Tahun 2009, mulai mengajar sebagai dosen Studio Perancangan Arsitektur 1 – 5 dan beberapa mata kuliah lainnya di Unikom, Bandung. Di tahun 2011 hingga awal 2015, aktif mengajar mata kuliah Studio Perancangan Arsitektur 1 – 6 dan Teknologi Bangunan 1 – 3 di Universitas Pancasila, Jakarta. Di pertengahan tahun 2015 hingga kini, menjadi dosen pengajar tetap (mengajar beberapa mata kuliah utama) dan ketua program studi Arsitektur Universitas Matana."
    },
    {
      "image": "/static/images/manajemen/d7.jpg",
      "title": "Triandi Pradana S.Tr.Par., M.Par",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d8.jpg",
      "title": "Ary Budi Warsito, S.Kom., M.Kom.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d9.jpg",
      "title": "JOSUA TIMOTIUS MANIK, S.Pd., M.Si.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d10.jpg",
      "title": "Jacob Steve Seleky., S.Si, M.Si, M.A",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d11.jpg",
      "title": "Florencia Irena Lawita, S.E., M.Ak.,  M.M., Cert. DA.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d12.jpg",
      "title": "Fifit Eka Furi Astutik., S.KM., M.Kes",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
    {
      "image": "/static/images/manajemen/d13.jpg",
      "title": "Dr. Anton PW. Nomleni, S.E, M.M.",
      "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sed facilisis nunc. Donec eget orci tortor. Ut efficitur egestas quam, nec aliquet urna euismod et. Nunc maximus nisl dui, id pellentesque felis facilisis quis. Aliquam rutrum pellentesque metus, et cursus nibh imperdiet in. Suspendisse risus diam, pretium id accumsan non, interdum vel sapien. Nullam sed metus nec mauris pretium molestie at sed libero. Duis eget vehicula dui, id convallis mi. Integer elementum cursus lectus, vel consectetur nibh volutpat sed. In iaculis libero est, at tempor augue porttitor non. Suspendisse a nunc rhoncus mauris sagittis auctor et eget massa. Aenean rutrum urna sit amet laoreet blandit."
    },
  ],
            'order': 3
        }
    ]
    
    create_standardized_blocks(management_page, default_blocks)
    return management_page

@togglable_cache()
def management_view(request):
    """View for management page"""
    try:
        management_page = Page.objects.get(
            slug='manajemen',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        management_page = create_default_management_page()
    
    # Get content blocks
    blocks = {}
    for block in management_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content
    
    context = {
        'page': management_page,
        'meta': management_page.metadata,
        'blocks': blocks, 'blocks_popup': { i.identifier: i.content for i in Page.objects.get(slug='popup', status=Page.PUBLISHED).content_blocks.all().order_by('order')  }
    }
    
    return render(request, 'pages/management.html', context)

def create_default_ukm_page():
    """Create default UKM page with standardized content blocks"""
    ukm_page = Page.objects.create(
        title="Unit Kegiatan Mahasiswa",
        slug="ukm",
        template='ukm.html',
        status=Page.PUBLISHED,
        metadata={
            'meta_description': 'Unit Kegiatan Mahasiswa (UKM) Matana University',
            'meta_keywords': 'ukm matana, kegiatan mahasiswa, organisasi mahasiswa'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Unit Kegiatan Mahasiswa',
            'subtitle': 'Mengembangkan Bakat dan Potensi Mahasiswa Melalui Berbagai Kegiatan',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1
        },
        {
            'identifier': 'olahraga_section',
            'title': 'UKM Olahraga',
            'description': 'Mengembangkan prestasi di bidang olahraga',
            'items': [
                {
                    'title': 'Basket',
                    'image': '/static/images/ukm1.jpg',
                },
                {
                    'title': 'Futsal',
                    'image': '/static/images/ukm2.jpg',
                },
                {
                    'title': 'Badminton',
                    'image': '/static/images/ukm3.jpg',
                }
            ],
            'order': 2
        },
        {
            'identifier': 'seni_section',
            'title': 'UKM Seni & Budaya',
            'description': 'Melestarikan dan mengembangkan seni budaya',
            'items': [
                {
                    'title': 'Paduan Suara',
                    'image': '/static/images/ukm3.jpg',
                },
                {
                    'title': 'Tari Tradisional',
                    'image': '/static/images/ukm2.jpg',
                },
                {
                    'title': 'Paduan Suara',
                    'image': '/static/images/ukm3.jpg',
                },
                {
                    'title': 'Tari Tradisional',
                    'image': '/static/images/ukm2.jpg',
                },
                {
                    'title': 'Modern Dance',
                    'image': '/static/images/ukm1.jpg',
                }
            ],
            'order': 3
        },
        {
            'identifier': 'akademik_section',
            'title': 'UKM Akademik & Profesional',
            'description': 'Meningkatkan kemampuan akademik dan profesional',
            'items': [
                {
                    'title': 'English Club',
                    'image': '/static/images/ukm2.jpg',
                },
                {
                    'title': 'Programming Club',
                    'image': '/static/images/ukm1.jpg',
                },
                {
                    'title': 'Entrepreneurship Club',
                    'image': '/static/images/ukm2.jpg',
                }
            ],
            'order': 4
        },
        {
            'identifier': 'minat_section',
            'title': 'UKM Minat Khusus',
            'description': 'Mengembangkan minat dan bakat khusus',
            'items': [
                {
                    'title': 'Photography Club',
                    'image': '/static/images/ukm1.jpg',
                },
                {
                    'title': 'Jurnalistik',
                    'image': '/static/images/ukm1.jpg',
                },
                {
                    'title': 'Pecinta Alam',
                    'image': '/static/images/ukm1.jpg',
                }
            ],
            'order': 5
        }
    ]
    
    create_standardized_blocks(ukm_page, default_blocks)
    return ukm_page

def ukm_view(request):
    """View for UKM page"""
    try:
        ukm_page = Page.objects.get(
            slug='ukm',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        ukm_page = create_default_ukm_page()
    
    # Get content blocks
    blocks = {}
    for block in ukm_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content
    
    context = {
        'page': ukm_page,
        'meta': ukm_page.metadata,
        'blocks': blocks, 'blocks_popup': { i.identifier: i.content for i in Page.objects.get(slug='popup', status=Page.PUBLISHED).content_blocks.all().order_by('order')  }
    }
    
    return render(request, 'pages/ukm.html', context)

def create_default_exchange_page():
    """Create default Student Exchange page with standardized content blocks"""
    exchange_page = Page.objects.create(
        title="Student Exchange",
        slug="student-exchange",
        template='exchange.html',
        status=Page.PUBLISHED,
        metadata={
            'meta_description': 'Program Student Exchange Matana University - Pengalaman Belajar Internasional',
            'meta_keywords': 'student exchange matana, pertukaran pelajar, studi internasional'
        }
    )
    
    default_blocks = [
        {
            'identifier': 'hero_section',
            'title': 'Student Exchange Program',
            'subtitle': 'Perluas Wawasan Global Anda Melalui Program Pertukaran Pelajar',
            'background_image': '/static/images/campus-aerial.jpg',
            'order': 1
        },
        {
            'identifier': 'asia_section',
            'title': 'Partner Universities in Asia',
            'description': 'Universitas mitra kami di kawasan Asia',
            'items': [
                {
                    'image': '/static/images/ex1.jpg',
                },
                {
                    'image': '/static/images/ex2.jpg',
                },
                {
                    'image': '/static/images/ex4.jpg',
                },
                {
                    'image': '/static/images/ex3.jpg',
                },
                {
                    'image': '/static/images/ex1.jpg',
                },
                {
                    'image': '/static/images/ex4.jpg',
                }
            ],
            'order': 2
        },
        {
            'identifier': 'europe_section',
            'title': 'Partner Universities in Europe',
            'description': 'Universitas mitra kami di kawasan Eropa',
            'items': [
                {
                    'image': '/static/images/univ-europe1.jpg',
                },
                {
                    'image': '/static/images/univ-europe2.jpg',
                },
                {
                    'image': '/static/images/univ-europe3.jpg',
                }
            ],
            'order': 3
        },
        {
            'identifier': 'program_section',
            'title': 'Program Unggulan',
            'description': 'Program pertukaran pelajar yang tersedia',
            'items': [
                {
                    'image': '/static/images/exchange1.jpg',
                },
                {
                    'image': '/static/images/exchange2.jpg',
                },
                {
                    'image': '/static/images/exchange3.jpg',
                }
            ],
            'order': 4
        },
        {
            'identifier': 'testimonial_section',
            'title': 'Alumni Exchange',
            'description': 'Kisah sukses alumni program pertukaran pelajar',
            'items': [
                {
                    'image': '/static/images/exa1.jpg',
                },
                {
                    'image': '/static/images/exa2.jpg',
                },
                {
                    'image': '/static/images/exa3.jpg',
                }
            ],
            'order': 5
        }
    ]
    
    create_standardized_blocks(exchange_page, default_blocks)
    return exchange_page

def exchange_view(request):
    """View for Student Exchange page"""
    try:
        exchange_page = Page.objects.get(
            slug='student-exchange',
            status=Page.PUBLISHED
        )
    except Page.DoesNotExist:
        exchange_page = create_default_exchange_page()
    
    # Get content blocks
    blocks = {}
    for block in exchange_page.content_blocks.all().order_by('order'):
        blocks[block.identifier] = block.content
    
    context = {
        'page': exchange_page,
        'meta': exchange_page.metadata,
        'blocks': blocks, 'blocks_popup': { i.identifier: i.content for i in Page.objects.get(slug='popup', status=Page.PUBLISHED).content_blocks.all().order_by('order')  }
    }
    
    return render(request, 'pages/exchange.html', context)

@login_required
def user_profile_view(request):
    """View for user profile page"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('user_profile')

    context = {
        'title': 'User Profile',
        'subtitle': 'Manage your account settings'
    }
    return render(request, 'admin/user_profile.html', context)

def logout_view(request):
    """View for handling logout"""
    logout(request)
    return redirect('home')


def get_related_articles(prodi_slug, limit=3):
    """
    Helper function to get related articles for a specific program study
    """
    try:
        # Get articles from the last 6 months
        six_months_ago = timezone.now() - timedelta(days=180)
        
        # Base queryset
        articles = Article.objects.filter(
            status='published',
            created_at__gte=six_months_ago
        )
        
        # Get articles with matching category or tags
        related = articles.filter(
            Q(category__slug__icontains=prodi_slug) |
            Q(tags__name__icontains=prodi_slug) |
            Q(title__icontains=prodi_slug) |
            Q(content__icontains=prodi_slug)
        ).distinct()

        # If not enough related articles, get latest articles
        if related.count() < limit:
            additional_needed = limit - related.count()
            latest_articles = articles.exclude(
                id__in=related.values_list('id', flat=True)
            )[:additional_needed]
            
            # Combine querysets
            related = (related | latest_articles).distinct()

        return related.order_by('-created_at')[:limit]
    
    except Exception as e:
        print(f"Error getting related articles: {str(e)}")
        return Article.objects.filter(status='published')[:limit]

@require_POST
@login_required
def delete_page(request, slug):
    try:
        page = Page.objects.get(slug=slug)
        page.delete()
        return JsonResponse({'success': True})
    except Page.DoesNotExist:
        return JsonResponse({'error': 'Page not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# import path
from pathlib import Path
from django.urls import path, include

@superuser_required
@require_safe
def secure_file_browser(request, token, subpath=''):
    """
    View for browsing and downloading files in a secure way.
    Only accessible by superusers with a valid token.
    
    Args:
        token (str): The token to validate access
        subpath (str): The subdirectory path relative to DOWNLOAD_ROOT
    """
    try:
        # Validate token
        token_obj = get_object_or_404(DownloadToken, token=token, is_active=True)
        if token_obj.is_expired():
            logger.warning(f"User {request.user.username} attempted to use expired token: {token}")
            raise PermissionDenied("This download link has expired.")
        
        # Get download root from settings
        download_root = getattr(settings, 'SECURE_DOWNLOAD_ROOT', None)
        if not download_root:
            logger.error("SECURE_DOWNLOAD_ROOT not configured in settings")
            return HttpResponse("Server configuration error", status=500)
        
        # Prevent path traversal
        current_path = safe_join_paths(download_root, subpath) if subpath else Path(download_root)
        if current_path is None:
            logger.warning(f"Path traversal attempt by {request.user.username}: {subpath}")
            raise PermissionDenied("Invalid path")
        
        # Check if path exists
        if not os.path.exists(current_path):
            logger.error(f"Path does not exist: {current_path}")
            raise Http404("The requested path does not exist")
        
        # If it's a file, serve it directly
        if os.path.isfile(current_path):
            return serve_file(request, current_path)
        
        # Otherwise, show directory listing
        return directory_listing(request, download_root, current_path, token, subpath)
        
    except DownloadToken.DoesNotExist:
        logger.warning(f"Invalid token used: {token}")
        raise PermissionDenied("Invalid download token")
    except Exception as e:
        logger.exception(f"Error in secure_file_browser: {e}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('admin:index')

def serve_file(request, file_path):
    """Serve a file for download"""
    try:
        # Determine the file's MIME type
        content_type, encoding = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
        
        # Check if file exists and is accessible
        if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
            logger.error(f"File not found or not readable: {file_path}")
            raise Http404("File not found or not readable")
        
        # Use FileResponse for efficient file streaming
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=os.path.basename(file_path)
        )
        
        logger.info(f"User {request.user.username} downloaded file: {file_path}")
        return response
        
    except Exception as e:
        logger.exception(f"Error serving file {file_path}: {e}")
        messages.error(request, f"Error serving file: {str(e)}")
        raise Http404("Error serving file")

def directory_listing(request, base_path, current_path, token, subpath):
    """Generate a directory listing page"""
    try:
        # Get list of files and directories
        items = []
        for name in sorted(os.listdir(current_path)):
            item_path = os.path.join(current_path, name)
            file_data = get_file_details(item_path)
            if file_data:
                # Add relative path for navigation
                rel_path = os.path.join(subpath, name) if subpath else name
                file_data['rel_path'] = rel_path.replace('\\', '/')  # Normalize path for URLs
                file_data['size_formatted'] = format_size(file_data['size'])
                file_data['modified_formatted'] = datetime.fromtimestamp(file_data['modified']).strftime('%Y-%m-%d %H:%M:%S')
                items.append(file_data)
        
        # Sort items: directories first, then files
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        # Prepare breadcrumbs for navigation
        breadcrumbs = []
        path_parts = subpath.split('/') if subpath else []
        for i, part in enumerate(path_parts):
            if part:  # Skip empty parts
                path = '/'.join(path_parts[:i+1])
                breadcrumbs.append({'name': part, 'path': path})
        
        context = {
            'files': items,
            'current_dir': os.path.basename(current_path) or 'Root',
            'parent_dir': os.path.dirname(subpath) if subpath else None,
            'token': token,
            'breadcrumbs': breadcrumbs,
            'is_root': not subpath,
            'title': f"File Browser - {os.path.basename(current_path) or 'Root'}",
        }
        
        return TemplateResponse(request, 'admin/file_browser.html', context)
        
    except Exception as e:
        logger.exception(f"Error listing directory {current_path}: {e}")
        messages.error(request, f"Error listing directory: {str(e)}")
        raise Http404("Error listing directory")

def format_size(size_bytes):
    """Format file size in human-readable form"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

@superuser_required
def manage_download_tokens(request):
    """View to manage download tokens"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            description = request.POST.get('description', '')
            token = DownloadToken.create_new_token(description=description)
            messages.success(request, f"New token created: {token.token}")
        
        elif action == 'delete':
            token_id = request.POST.get('token_id')
            if token_id:
                try:
                    token = DownloadToken.objects.get(id=token_id)
                    token.delete()
                    messages.success(request, "Token deleted successfully")
                except DownloadToken.DoesNotExist:
                    messages.error(request, "Token not found")
        
        elif action == 'toggle':
            token_id = request.POST.get('token_id')
            if token_id:
                try:
                    token = DownloadToken.objects.get(id=token_id)
                    token.is_active = not token.is_active
                    token.save()
                    status = "activated" if token.is_active else "deactivated"
                    messages.success(request, f"Token {status} successfully")
                except DownloadToken.DoesNotExist:
                    messages.error(request, "Token not found")
    
    # Get all tokens
    tokens = DownloadToken.objects.all().order_by('-created_at')
    
    context = {
        'tokens': tokens,
        'title': 'Manage Download Tokens',
    }
    
    return TemplateResponse(request, 'admin/download_tokens.html', context)

@login_required
@superuser_required
def backup_api_view(request):
    """
    API endpoint for triggering project backups, especially for background processing.
    Only accessible to superusers.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        
        backup_name = data.get('backup_name', '')
        run_in_background = data.get('background', False)
        token = data.get('token', '')
        
        # Set default directories to exclude based on parameters
        exclude_dirs = []
        if not data.get('include_db', True):
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            exclude_dirs.append(db_path)
        
        if not data.get('include_media', True):
            media_path = settings.MEDIA_ROOT
            exclude_dirs.append(media_path)
        
        if run_in_background:
            # Run backup in a separate thread to avoid blocking the request
            backup_thread = threading.Thread(
                target=_perform_backup_in_background,
                args=(backup_name, DEFAULT_EXCLUDES, exclude_dirs, token)
            )
            backup_thread.daemon = True  # Thread will exit when main process exits
            backup_thread.start()
            
            return JsonResponse({
                'success': True,
                'message': 'Backup started in background',
                'background': True
            })
        else:
            # Run backup synchronously
            result = create_project_backup(
                backup_name=backup_name,
                exclude_patterns=DEFAULT_EXCLUDES,
                exclude_dirs=exclude_dirs
            )
            
            if result['success']:
                response_data = {
                    'success': True,
                    'filename': result['filename'],
                    'size': result['size'],
                    'path': os.path.basename(result['path'])
                }
                
                # Add download URL if a token was provided
                if token:
                    try:
                        if DownloadToken.objects.filter(token=token, is_active=True).exists():
                            backup_relpath = os.path.relpath(
                                result['path'], 
                                settings.SECURE_DOWNLOAD_ROOT
                            )
                            download_url = reverse('secure_file_browser', kwargs={
                                'token': token,
                                'subpath': backup_relpath
                            })
                            response_data['download_url'] = request.build_absolute_uri(download_url)
                    except Exception as e:
                        logger.error(f"Error generating download URL: {str(e)}")
                
                return JsonResponse(response_data)
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Unknown error occurred')
                }, status=500)
    
    except Exception as e:
        logger.exception(f"Unexpected error in backup_api_view: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def _perform_backup_in_background(backup_name, exclude_patterns, exclude_dirs, token=None):
    """
    Helper function to perform backup in a background thread.
    
    Args:
        backup_name (str): Name for the backup file
        exclude_patterns (list): Patterns to exclude
        exclude_dirs (list): Directories to exclude
        token (str): Optional token ID for creating download URL
    """
    try:
        logger.info(f"Starting background backup: {backup_name}")
        
        result = create_project_backup(
            backup_name=backup_name,
            exclude_patterns=exclude_patterns,
            exclude_dirs=exclude_dirs
        )
        
        if result['success']:
            logger.info(f"Background backup completed successfully: {result['filename']}")
        else:
            logger.error(f"Background backup failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.exception(f"Error in background backup process: {str(e)}")

import subprocess
import json
from django.http import JsonResponse
from django.conf import settings
from .utils import superuser_required  # Decorator superuser_required yang sudah Anda punya


@superuser_required
def git_pull_page_view(request):
    """
    View untuk menampilkan halaman admin git pull.
    """
    return render(request, 'admin/git_pull.html')

@superuser_required
def git_pull_view(request):
    """
    Endpoint untuk menjalankan 'git pull' pada direktori project.
    Hanya bisa diakses oleh superuser.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed. Use POST.'}, status=405)

    try:
        # Jalankan git pull di direktori BASE_DIR project Django
        process = subprocess.run(
            ['git', 'pull'],
            cwd=settings.BASE_DIR,  # Penting: cwd=BASE_DIR
            capture_output=True,
            text=True,
            check=False  # Jangan raise exception jika return code != 0, kita handle sendiri
        )

        output = process.stdout
        error_output = process.stderr
        return_code = process.returncode

        if return_code == 0:
            log_message = f"Git pull berhasil dijalankan oleh user {request.user.username}:\nOutput:\n{output}"
            logger.info(log_message) # Log info jika berhasil
            return JsonResponse({
                'success': True,
                'message': 'Git pull berhasil!',
                'output': output,
                'error': error_output
            })
        else:
            error_message = f"Git pull GAGAL dijalankan oleh user {request.user.username}:\nReturn Code: {return_code}\nOutput:\n{output}\nError Output:\n{error_output}"
            logger.error(error_message) # Log error jika gagal
            return JsonResponse({
                'success': False,
                'error': 'Git pull gagal!',
                'output': output,
                'error_output': error_output
            }, status=500) # Status 500 untuk error server

    except Exception as e:
        error_message = f"Error saat menjalankan git pull oleh user {request.user.username}: {str(e)}"
        logger.exception(error_message) # Log exception lengkap
        return JsonResponse({
            'success': False,
            'error': f'Terjadi kesalahan server: {str(e)}'
        }, status=500)

@staff_member_required
def toggle_popup_view(request):
    """Toggle the visibility of the popup"""
    try:
        popup_page = Page.objects.get(slug='popup', status=Page.PUBLISHED)
        metadata = popup_page.metadata
        
        # Toggle is_active value
        is_active = metadata.get('is_active', False)
        metadata['is_active'] = not is_active
        popup_page.metadata = metadata
        popup_page.save()
        
        status = "activated" if metadata['is_active'] else "deactivated"
        messages.success(request, f"Popup has been {status}")
    except Page.DoesNotExist:
        messages.error(request, "Popup page does not exist")
    
    # Redirect back to the referring page or to cache management if no referrer
    referrer = request.META.get('HTTP_REFERER', None)
    if referrer:
        return redirect(referrer)
    return redirect('cache_management')