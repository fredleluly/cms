"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from apps.pages.views import (
    home_view, page_view, news_view, article_detail_view, 
    dashboard_view, article_create_view, article_edit_view,
    article_save_view, article_delete_view, article_quick_update,
    profile_view, category_create_view, upload_image, article_list_view, bulk_action_view,
    registration_view, registration_submit, scholarship_view, page_edit_view, page_list_view,
    mitra_view, management_view, ukm_view, exchange_view, profile_view_manajemen,
    user_profile_view, logout_view, delete_page
)
from apps.pages.views import *
from django.contrib.sitemaps.views import sitemap
from apps.pages.sitemaps import ArticleSitemap, StaticViewSitemap
from django.views.generic import TemplateView
from .sitemap import StaticViewSitemap
from django.views.static import serve
from django.contrib.auth.decorators import login_required


# Define sitemaps dictionary before using it
sitemaps = {
    'articles': ArticleSitemap,
    'static': StaticViewSitemap,
}

from django.shortcuts import render

def test_404(request):
    """View untuk testing halaman 404"""
    return render(request, '404.html', status=200)

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path(settings.SECRET_KEY_LOGIN+"_"+'admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('matana-news/', news_view, name='news'),
    path('profil-matana/', profile_view, name='profile'),
    path('dashboard/content/', dashboard_view, name='content_dashboard'),
    path('dashboard/content/create/', article_create_view, name='article_create'),
    path('dashboard/content/<int:pk>/edit/', article_edit_view, name='article_edit'),
    path('dashboard/content/save/', article_save_view, name='article_save'),
    path('dashboard/content/<int:pk>/delete/', article_delete_view, name='article_delete'),
    path('dashboard/content/<int:pk>/quick-update/', article_quick_update, name='article_quick_update'),
    path('dashboard/content/category/create/', category_create_view, name='category_create'),
    path('matana-news/<slug:slug>/', article_detail_view, name='article_detail'),
    path('upload/image/', upload_image, name='upload_image'),
    path('dashboard/content/articles/', article_list_view, name='article_list'),
    path('dashboard/content/bulk-action/', bulk_action_view, name='bulk_action'),
    path('pendaftaran/', registration_view, name='registration'),
    path('pendaftaran/submit/', registration_submit, name='registration_submit'),
    path('beasiswa/', scholarship_view, name='scholarship'),
    path('test-404/', test_404, name='test_404'),
    path('lib/', include('apps.media.urls')),
    path('pedoman-akademik/', PedomanAkademikView.as_view(), name='pedoman_akademik'),
    path('kalender-akademik/', KalenderAkademikView.as_view(), name='kalender_akademik'),
    path('dashboard/pages/<slug:slug>/edit/', page_edit_view, name='page_edit'),
    path('dashboard/pages/', page_list_view, name='page_list'),
    path('dashboard/pages/<slug:slug>/delete/', delete_page, name='delete_page'),
    path("django-check-seo/", include("django_check_seo.urls")),
    path('mitra/', mitra_view, name='mitra'),
    path('manajemen/', management_view, name='management'),
    path('ukm/', ukm_view, name='ukm'),
    path('prodi/manajemen/', profile_view_manajemen, name='manajemen'),
    path('prodi/manajemens2/', profile_view_manajemens2, name='manajemens2'),
    path('prodi/akuntansi/', profile_view_akuntansi, name='akuntansi'),
    path('prodi/hospar/', profile_view_hospitality, name='hospar'),
    path('prodi/dkv/', profile_view_dkv, name='dkv'),
    path('prodi/arsitektur/', profile_view_arsitektur, name='arsitektur'),
    path('prodi/k3/', profile_view_k3, name='k3'),
    path('prodi/fisika-medis/', profile_view_fisika_medis, name='fisika_medis'),
    path('prodi/statistika/', profile_view_statistika, name='statistika'),
    path('prodi/informatika/', profile_view_informatika, name='informatika'),
    path('student-exchange/', exchange_view, name='exchange'),
    path('dashboard/profile/', user_profile_view, name='user_profile'),
    path('logout/', logout_view, name='logout'),
    path('secure-files/<str:token>/', secure_file_browser, name='secure_file_browser'),
    path('secure-files/<str:token>/<path:subpath>', secure_file_browser, name='secure_file_browser'),
    
    # Token management (only accessible to superusers)
    path('admin/download-tokens/', manage_download_tokens, name='manage_download_tokens'),
    
]
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # path("__reload__/", include("django_browser_reload.urls")),
    # path('<slug:slug>/', page_view, name='page_view'),


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#  Add this after urlpatterns
if settings.DEBUG:
    urlpatterns += [
        path('404/', lambda request: views.custom_404(request, None)),
    ]

handler404 = 'apps.pages.views.custom_404'
