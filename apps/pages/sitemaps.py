from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Page

class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ['home', 'news', 'profile']

    def location(self, item):
        return reverse(item) 