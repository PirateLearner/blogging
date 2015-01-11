from django.utils import timezone
import sys
from django.db import models
from django.db.models import Q

from django.contrib import auth
from mptt.models import MPTTModel, TreeForeignKey
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager
from taggit.models import TaggedItem, Tag

from django.conf import settings

if 'cms' in settings.INSTALLED_APPS:
    try:
        from cms.models.pluginmodel import CMSPlugin
        from djangocms_text_ckeditor.models import Text
    except ImportError:
        print 'CMS not installed'
    
from blogging.utils import get_imageurl_from_data, strip_image_from_data, truncatewords
from blogging.tag_lib import strip_tag_from_data
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
import traceback

#from django.contrib.contenttypes.generic import GenericRelation

#from south.v2 import DataMigration

# Create your models here.

LATEST_PLUGIN_TEMPLATES = (
  ('blogging/plugin/plugin_teaser.html', 'Teaser View'),
  ('blogging/plugin/plugin_section.html', 'Section View'),
  ('blogging/plugin/sidebar_list.html', 'Text List'),
  ('blogging/plugin/teaser_list.html', 'Stacked List'),
)
 

class RelatedManager(models.Manager):

    def get_query_set(self):
        qs = super(RelatedManager, self).get_query_set()
        return qs

    def get_tags(self, language):
        """Returns tags used to tag post and its count. Results are ordered by count."""

        # get tagged post
        entries = self.get_query_set().distinct()
        if not entries:
            return []
        kwargs = TaggedItem.bulk_lookup_kwargs(entries)

        # aggregate and sort
        counted_tags = dict(TaggedItem.objects
                                      .filter(**kwargs)
                                      .values('tag')
                                      .annotate(count=models.Count('tag'))
                                      .values_list('tag', 'count'))

        # and finally get the results
        tags = Tag.objects.filter(pk__in=counted_tags.keys())
        for tag in tags:
            tag.count = counted_tags[tag.pk]
        return sorted(tags, key=lambda x: -x.count)

class PublishedManager(RelatedManager):
    def get_query_set(self):
        qs = super(PublishedManager, self).get_query_set()
        now = timezone.now()
        qs = qs.filter(publication_start__lte=now)
        qs = qs.filter(Q(published_flag=True))
        return qs


class BlogContentType(models.Model):
    content_type = models.CharField(max_length = 100,unique = True)
    is_leaf = models.BooleanField('Is leaf node?', default = 0)

    def __unicode__(self):
        return self.content_type

class BlogParent(MPTTModel):
    title = models.CharField(max_length = 50, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    data = models.TextField(null= False)
    content_type = models.ForeignKey(BlogContentType,null=True,default=None)
    slug = models.SlugField()
    def __unicode__(self):
        return self.title
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        blogs = BlogContent.objects.filter(section=self.parent)
        if blogs:
            try:
                orphan_parent = BlogParent.objects.get(title='Orphan')
                for blog in blogs:
                    blog.section = orphan_parent
                    blog.save()
            except:
                print 'FATAL ERROR CAN DO NOTHING'            
        super(BlogParent, self).save(*args, **kwargs)
    
    def form_url(self):
        parent_list = self.get_ancestors(include_self=True)
        return_path = '/'.join(word.slug for word in parent_list)
        #print "inside absolute URL ", return_path
        return return_path
    
    def get_image_url(self):
        image = get_imageurl_from_data(self.data)
        print image 
        return image
    
    def get_absolute_url(self):
        kwargs = {'slug': str(self.form_url())}
        return reverse('blogging:teaser-view', kwargs=kwargs)
    def get_menu_title(self):
        return self.title
    class MPTTMeta:
            order_insertion_by = ['title']


class BlogContent(models.Model):
    title = models.CharField(max_length = 100)
    create_date = models.DateTimeField('date created', auto_now_add=True)
    author_id  = models.ForeignKey(auth.models.User, related_name="blogcontent")
    data = models.TextField(null= False)
    published_flag = models.BooleanField('is published?',default = 1)
    special_flag = models.BooleanField(default = 0)
    last_modified = models.DateTimeField('date modified',auto_now=True)
    url_path = models.CharField(max_length= 255)
    section = models.ForeignKey(BlogParent, limit_choices_to={'children': None})
    content_type = models.ForeignKey(BlogContentType,null=True)
    slug = models.SlugField(max_length= 100)
    tags = TaggableManager(blank=True)
    publication_start = models.DateTimeField(('Published Since'), default=timezone.now, help_text=('Used for automatic delayed publication. For this feature to work published_flag must be on.'))
    objects = RelatedManager()    
    published = PublishedManager()
    
    #annotation = GenericRelation(Annotation, content_type_field='content_type', object_id_field='object_pk')

    def get_absolute_url(self):
        kwargs = {'slug': self.url_path,}
        print "LOGS:: Fetching URI for node"
        return reverse('blogging:teaser-view', kwargs=kwargs)
    
    def get_image_url(self):
        image =  get_imageurl_from_data(self.data)
        print "LOGS:: Fetching Image for node"
        if image:
            print image
            return image
        else:
            return self.section.get_image_url()

    def get_summary(self):
        summary = self.data
        print "LOGS:: Fetching Node summary"
        summary = strip_tag_from_data(summary)
        summary = strip_image_from_data(summary)
        summary = strip_tags(summary)
        summary = truncatewords(summary, 150)
        return summary
    
    def get_title(self):
        return self.title
    
    
    def find_path(self,section): 
        parent_list = section.get_ancestors(include_self=True)
        return_path = '/'.join(word.slug for word in parent_list)
        return_path = return_path + str("/") + self.slug + str("/") + str(self.id)
        print return_path
        return return_path

    def get_menu_title(self):
        return self.title

    def get_parent(self):
        return self.section

    def get_tags(self):
        tags = self.tags.all()
        tag_list = []
        print "LOGS:Get Tags Called for ", self.title
        print "LOGS: tags are ", tags
        for tag in tags:
            print "LOGS: hey there!!!"
            try:
                tmp = {}
                tmp['name'] = tag.name
                kwargs = {'tag': tag.name,}
                tmp['url'] = reverse('blogging:tagged-posts',kwargs=kwargs)
                print "LOGS: TAG NAME ", tmp['name'],"URL ", tmp['url']
                tag_list.append(tmp)
                print "LOGS: Printing tags ", tmp
            except:
                print "Unexpected error:", sys.exc_info()[0]
                for frame in traceback.extract_tb(sys.exc_info()[2]):
                    fname,lineno,fn,text = frame
                    print "Error in %s on line %d" % (fname, lineno)
        return tag_list
    
    def get_author(self):
        print self.author_id
        return self.author_id
        #return self.author_id.first_name or self.author_id.username  

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(BlogContent, self).save(*args, **kwargs)
        self.url_path = self.find_path(self.section)
        super(BlogContent, self).save(*args, **kwargs)
        print "after save "  + self.url_path

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publication_start']


if 'cms' in settings.INSTALLED_APPS:
    class LatestEntriesPlugin(CMSPlugin):
    
        latest_entries = models.IntegerField(default=5, help_text=('The number of latests entries to be displayed.'))
        parent_section = models.ForeignKey(BlogParent,null=True,blank=True)
        tags = models.ManyToManyField('taggit.Tag', blank=True, help_text=('Show only the blog posts tagged with chosen tags.'))
        template = models.CharField('Template', max_length=255,
                                    choices = LATEST_PLUGIN_TEMPLATES, default='blogging/plugin/plugin_teaser.html')
        def __unicode__(self):
            return str(self.latest_entries)
    
        def copy_relations(self, oldinstance):
            self.tags = oldinstance.tags.all()
    
        def get_posts(self):
            if self.parent_section:
                if self.parent_section.is_leaf_node():
                    posts = BlogContent.published.filter(section=self.parent_section)
                    print 'parent is leaf node'
                else:
                    print 'parent is non leaf node'
                    parent_list = self.parent_section.get_descendants()
                    print 'parent list is ', parent_list
                    posts = BlogContent.published.filter(section__in=parent_list)
            else:
                posts = BlogContent.published.all()
            
            tags = list(self.tags.all())
            if tags:
                posts = posts.filter(tags__in=tags)
            return posts[:self.latest_entries]
        
        def get_section(self):
            return self.parent_section
    
        
        
    class SectionPlugin(CMSPlugin):
    
        section_count = models.IntegerField(default=None, blank=True,null=True, help_text=('The number of sections to be displayed.'))
        parent_section = models.ForeignKey(BlogParent,null=True,blank=True)
    
        def __unicode__(self):
            return str(self.section_count)
    
        def get_sections(self):
            if self.parent_section:
                sections = self.parent_section.get_children()
            else:
                sections = BlogParent.objects.all(~Q(title='Orphan'),level=0)
            if self.section_count:
                return sections[:self.section_count]
            return sections
    
    class ContactPlugin(CMSPlugin):
        to_email = models.EmailField(default= 'captain@piratelearner.com')
        thanks_text = models.CharField(max_length=100,default = 'Thanks for reaching out to Us. We will get back to you soon.')
        def __unicode__(self):
            return 'ContactPlugin'
        def thanks(self):
            return self.thanks_text
            
"""
class Migration(DataMigration):
	def forwards(self, orm):
        	"Write your forwards methods here."
        	BlogParent.objects.rebuild()
"""
