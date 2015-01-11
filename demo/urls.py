from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     url(r'^$', 'demo.views.home', name='home'),
     url(r'^contact/$', 'demo.views.contact', name='contact'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^blogging/', include('blogging.urls',namespace='blogging')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^admin/', include(admin.site.urls)),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
