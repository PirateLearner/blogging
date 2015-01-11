from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from blogging.models import BlogParent,BlogContentType,BlogContent
from blogging.forms import PostForm, ParentForm

from django.conf import settings

if 'cms' in settings.INSTALLED_APPS:
    try:
        from cms.admin.placeholderadmin import FrontendEditableAdmin, PlaceholderAdmin
    except ImportError:
        print 'CMS not installed'
    
import reversion

def mark_published(modeladmin, request, queryset):
    queryset.update(published_flag = 1)
mark_published.short_description = "Mark selected content as published"



class ParentAdmin(MPTTModelAdmin,reversion.VersionAdmin):
    fieldsets = [
                 ('',     {'fields': ['title', 'parent','slug','data','content_type']} ),
                 ]
    list_display = ('title', 'parent', 'level')
    list_filter = ['parent']
    search_fields = ['title']
    form = ParentForm
    ordering = ['title']
    prepopulated_fields = {'slug': ('title',), }

if 'cms' in settings.INSTALLED_APPS:
    class ContentAdmin(FrontendEditableAdmin,PlaceholderAdmin,reversion.VersionAdmin):
        list_display = ('title', 'create_date', 'published_flag','publication_start')
        list_filter = ['create_date']
        search_fields = ['title']
        ordering = ['title']
        actions = [mark_published]
        prepopulated_fields = {'slug': ('title',), }
        form = PostForm
        frontend_editable_fields = ('title', 'data')
        fieldsets = [
                     ('Info',     {'fields': ['title','slug', 'data','publication_start']} ),
                     ('Other',     {'fields': ['section', 'author_id', 'published_flag', 'special_flag', 'content_type','tags']} )
                     ]
        

admin.site.register(BlogParent, ParentAdmin)
admin.site.register(BlogContentType)
if 'cms' in settings.INSTALLED_APPS:
    admin.site.register(BlogContent,ContentAdmin)
