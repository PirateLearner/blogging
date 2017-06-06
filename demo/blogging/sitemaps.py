from django.contrib.sitemaps import Sitemap
from blogging.models import Content, Section
from django.utils import timezone
from django.db.models import Q


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return Content.published.all()

    def lastmod(self, obj):
        return obj.last_modified


class SectionSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        return Section.objects.all().filter(~Q(title='Orphan'))
    
    def lastmod(self,obj):
        return timezone.now()

