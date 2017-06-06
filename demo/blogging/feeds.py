'''
Created on 01-Jul-2016

@author: craft
'''
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse

from blogging.models import Content

import json
from django.utils.safestring import mark_safe

class LatestBlogEntiresFeed(Feed):
    title = "Latest blog posts feed"
    link = "/blogfeed/"
    description = "Blog Feed of latest blog entries."
    
    item_enclosure_mime_type = "application/xml"
    def items(self):
        return Content.objects.order_by('-publication_start')[:5]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        json_obj = json.loads(item.data)
        print json_obj['content']
        return mark_safe(json_obj['content'])