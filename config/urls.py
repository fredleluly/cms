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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.pages.views import (
    home_view, page_view, news_view, article_detail_view, 
    dashboard_view, article_create_view, article_edit_view,
    article_save_view, article_delete_view, article_quick_update,
    profile_view, category_create_view, upload_image, article_list_view, bulk_action_view,
    registration_view, registration_submit, scholarship_view
)
from django.contrib.sitemaps.views import sitemap
from apps.pages.sitemaps import ArticleSitemap, StaticViewSitemap
from django.views.generic import TemplateView
from .sitemap import StaticViewSitemap

# Define sitemaps dictionary before using it
sitemaps = {
    'articles': ArticleSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
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
    # path('<slug:slug>/', page_view, name='page_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
