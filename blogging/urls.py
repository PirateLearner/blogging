from django.conf.urls import patterns, url
import blogging.views as view
from blogging.forms import *

urlpatterns = patterns(
    '',
    url(r'^$', view.index, name='section-view'),
    url(r'^contact/$', view.ContactUs, name='contact-us'),
    url(r'^create-post/$', view.new_post, name='create-post'),
#    url(r'^create-content/$', view.ContentWizard.as_view([ContentTypeForm, ContentForm])),
    url(r'^content-type/$', view.content_type, name='content-type'),
    url(r'^add-model/(?P<model_name>[\w.+-/]+)/$', view.add_new_model, name='add-model-content-type'),
    url(r'^author/$', view.authors_list, name='author-list'),
    url(r'^author/(?P<slug>[\w.@+-]+)/(?P<post_id>\d+)$', view.author_post, name='author-posts'),
#    url(r'^feed/$', LatestEntriesFeed(), name='latest-posts-feed'),
    url(r'^(?P<year>\d{4})/$', view.archive, name='archive-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', view.archive, name='archive-month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', view.archive, name='archive-day'),
#    url(r'^(?P<slug>[\w.+-/]+)/(?P<post_id>\d+)$', view.detail, name='post-detail'),
    url(r'^tag/(?P<tag>[-\w]+)/$', view.tagged_post, name='tagged-posts'),
    url(r'^(?P<slug>[\w.+-/]+)/$', view.teaser, name='teaser-view'),
#    url(r'^(?P<slug>\D+)(?P<post_id>\d+)$', view.detail, name='post-detail'),
#    url(r'^(?P<path>\D*)$', view.teaser, name='teaser-view'),
#    url(r'^tag/$', TagsListView.as_view(), name='tag-list'),

#    url(r'^tag/(?P<tag>[-\w]+)/feed/$', TagFeed(), name='tagged-posts-feed'),
)
