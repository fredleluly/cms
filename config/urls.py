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
from apps.pages.views import home_view, page_view, news_view, article_detail_view, dashboard_view, article_create_view, article_edit_view, article_save_view, article_delete_view, article_quick_update

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('matana-news/', news_view, name='news'),
    path('dashboard/content/', dashboard_view, name='content_dashboard'),
    path('dashboard/content/create/', article_create_view, name='article_create'),
    path('dashboard/content/<int:pk>/edit/', article_edit_view, name='article_edit'),
    path('dashboard/content/save/', article_save_view, name='article_save'),
    path('dashboard/content/<int:pk>/delete/', article_delete_view, name='article_delete'),
    path('dashboard/content/<int:pk>/quick-update/', article_quick_update, name='article_quick_update'),
    path('matana-news/<slug:slug>/', article_detail_view, name='article_detail'),
    # path('<slug:slug>/', page_view, name='page_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
