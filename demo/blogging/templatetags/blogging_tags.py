"""
Template Tags for following functionalities:
    1. tag for rendering contact form.
    2. tag for rendering list of articles pending for editors approval.
"""
from copy import copy
from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import InclusionTag
from django import template
from blogging.tag_lib import get_field_name_from_tag
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.mail import  mail_admins
from blogging.forms import ContactForm
from django.template import RequestContext
from blogging.models import BlogContent
from taggit.models import Tag
from django.core.urlresolvers import reverse

import sys
import traceback
from django.http.response import HttpResponseForbidden


register = template.Library()

class ContentRender(InclusionTag):
    template = 'blogging/templatetags/render_content.html'
    name = 'render_content'
    options = Options(
        Argument('instance'),
        Argument('attribute', default=None, required=False),
    )

    def __init__(self, parser, tokens):
        self.parser = parser
        super(ContentRender, self).__init__(parser, tokens)
        
    def get_template(self, context, **kwargs):
        return self.template
    
    def render_tag(self, context, **kwargs):
        """
        Overridden from InclusionTag to push / pop context to avoid leaks
        """
        context.push()
        print "render tag is called"
        try:
            template = self.get_template(context, **kwargs)
            data = self.get_context(context, **kwargs)
            output = render_to_string(template, data)
#             print output
            context.pop()
            return output
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return "Http404"

        
    def _get_data_context(self,context,instance,attribute):
        extra_context = copy(context)
        if attribute:
            print "atrribute ", attribute
            extra_context['attribute_name'] = attribute.__str__()
            extra_context['attribute'] = getattr(instance, attribute, '')
        else:
            print "tag list ", instance.tag_list
            attribute_list = []
            for tag in instance.tag_list:
                if tag['name'] == "pid_count_tag":
                    continue
                attribute_name = get_field_name_from_tag(tag['name'])
                print "tag field name ", attribute_name
                attribute_value = getattr(instance, attribute_name, '')
                if attribute_name == 'title':
                    extra_context['title'] = attribute_value
                else:
                    attribute_list.append({'name':attribute_name,'value':attribute_value})
            print "attribute list ", attribute_list
            extra_context['attribute_list'] = attribute_list
        return extra_context
            

    def get_context(self, context,instance, attribute):
        extra_context = self._get_data_context(context, instance, attribute)
        return extra_context

class ContactTag(InclusionTag):
    template = 'blogging/includes/contact.html'
    name = 'render_contact_form'
#     options = Options(
#         Argument('template_name'),
#         Argument('count'),
#         Argument('base_parent', default=None, required=False),
#         Argument('tags', default=None, required=False),
#     )

    def __init__(self, parser, tokens):
        self.parser = parser
        super(ContactTag, self).__init__(parser, tokens)

    def get_template(self, context, **kwargs):
        return self.template

    
    def create_form(self, request):
        contact_type = request.GET.get('contact_type',None)
        
        
        if contact_type is None:
            contact_type = 'Queries'
        
        print "Contact form contact_type : ", contact_type
            
        if request.method == "POST":
            print "Contact form inside post"
            return ContactForm(data=request.POST)
        else:
            print "Contact form inside get"
            return ContactForm(initial={'contact_type':contact_type})    
    def render_tag(self, context, **kwargs):
        context.push()
        print "contact tag is called"
        try:
            request = context['request']
            form = self.create_form(request)
            instance = {}
            instance['thanks'] = 'Thanks for your time! We will get back to you soon.'
            template = self.get_template(context, **kwargs)

            if request.method == "POST" and form.is_valid():
                subject = 'Contact mail from PirateLearner( ' + form.cleaned_data['contact_type'] + ' )'
                message = 'Name: ' + form.cleaned_data['name'] + '\n' + 'email: ' + form.cleaned_data['email'] + '\n Body: ' + form.cleaned_data['content']
                mail_admins(subject, message, fail_silently=False)
                
                data = RequestContext(request, {
                                        'contact': instance,
                                      })
            else:
                data = RequestContext(request, {
                                        'contact': instance,
                                        'form': form,

                                      })
            output = render_to_string(template, data)
            context.pop()
            print output
            return output
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return "Http404"

class DraftTag(InclusionTag):
    template = 'blogging/templatetags/drafts.html'
    name = 'render_draft_articles'
    options = Options(
        Argument('user', default=None, required=False),
    )

    def __init__(self, parser, tokens):
        self.parser = parser
        super(DraftTag, self).__init__(parser, tokens)

    def get_template(self, context, **kwargs):
        return self.template

    
    def render_tag(self, context, **kwargs):
        context.push()
        print "draft tag is called"
        try:
            request = context['request']
            template = self.get_template(context, **kwargs)
            data = self._get_context(context, **kwargs)
            output = render_to_string(template, data)
            context.pop()
            print output
            return output
        except:
            print "Unexpected error:", sys.exc_info()[0]
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname,lineno,fn,text = frame
                print "Error in %s on line %d" % (fname, lineno)
            return "Http404"
    def _get_context(self,context, user):
        extra_context = {}
        if user:
            extra_context['drafts'] = BlogContent.objects.filter(published_flag=False,special_flag=True,author_id=user)
        else:
            extra_context['drafts'] = BlogContent.objects.filter(published_flag=False,special_flag=True)
        return extra_context  

class PendingTag(InclusionTag):
    template = 'blogging/templatetags/pending.html'
    name = 'render_pending_articles'
    options = Options(
        Argument('user', default=None, required=False),
    )
    def __init__(self, parser, tokens):
        self.parser = parser
        super(PendingTag, self).__init__(parser, tokens)
        
    def get_template(self, context, **kwargs):
        return self.template
    
    def render_tag(self, context, **kwargs):
        """
        Overridden from InclusionTag to push / pop context to avoid leaks
        """
        context.push()
        print "pendig tag is called"
        try:
            template = self.get_template(context, **kwargs)
            data = self.get_context(context, **kwargs)
            output = render_to_string(template, data)
#             print output
            context.pop()
            return output
        except:
            print "Unexpected error:", sys.exc_info()[0]
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname,lineno,fn,text = frame
                print "Error in %s on line %d" % (fname, lineno)
            
            return "Http404"

        
    def _get_data_context(self,context,user):
        extra_context = copy(context)
        if user:
            print "User ", user
            extra_context['pending'] = BlogContent.objects.filter(published_flag=False,special_flag=False,author_id=user)
            print "Printing pending articles ", extra_context['pending']
        else:
            extra_context['pending'] = BlogContent.objects.filter(published_flag=False,special_flag=False)
        return extra_context
            

    def get_context(self, context,user):
        extra_context = self._get_data_context(context,user)
        return extra_context


class ReviewTag(InclusionTag):
    template = 'blogging/templatetags/review.html'
    name = 'render_review_articles'
#     options = Options(
#         Argument('template_name'),
#         Argument('count'),
#         Argument('base_parent', default=None, required=False),
#         Argument('tags', default=None, required=False),
#     )

    def __init__(self, parser, tokens):
        self.parser = parser
        super(ReviewTag, self).__init__(parser, tokens)

    def get_template(self, context, **kwargs):
        return self.template

    
    def render_tag(self, context, **kwargs):
        context.push()
        print "draft tag is called"
        try:
            request = context['request']
            template = self.get_template(context, **kwargs)
            data = self._get_context(context, **kwargs)
            output = render_to_string(template, data)
            context.pop()
            print output
            return output
        except:
            print "Unexpected error:", sys.exc_info()[0]
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname,lineno,fn,text = frame
                print "Error in %s on line %d" % (fname, lineno)
            return "Http404"
    def _get_context(self,context, **kwargs):
        extra_context = {}
        extra_context['review'] = BlogContent.objects.filter(published_flag=False,special_flag=False)
        return extra_context  


class PublishedTag(InclusionTag):
    template = 'blogging/templatetags/published.html'
    name = 'render_published_articles'
    options = Options(
        Argument('user', default=None, required=False),
    )
    def __init__(self, parser, tokens):
        self.parser = parser
        super(PublishedTag, self).__init__(parser, tokens)
        
    def get_template(self, context, **kwargs):
        return self.template
    
    def render_tag(self, context, **kwargs):
        """
        Overridden from InclusionTag to push / pop context to avoid leaks
        """
        context.push()
        print "published tag is called"
        try:
            template = self.get_template(context, **kwargs)
            data = self.get_context(context, **kwargs)
            output = render_to_string(template, data)
#             print output
            context.pop()
            return output
        except:
            print "Unexpected error:", sys.exc_info()[0]
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname,lineno,fn,text = frame
                print "Error in %s on line %d" % (fname, lineno)
            
            return "Http404"

        
    def _get_data_context(self,context,user):
        extra_context = copy(context)
        if user:
            print "User ", user
            extra_context['published'] = BlogContent.objects.filter(published_flag=True,author_id=user)
            print "Printing published articles ", extra_context['published']
        else:
            extra_context['published'] = BlogContent.objects.filter(published_flag=True)
        return extra_context
            

    def get_context(self, context,user):
        extra_context = self._get_data_context(context,user)
        return extra_context


@register.assignment_tag
def get_blogging_tags():
    tags = Tag.objects.all()[:10]
    tag_list = []
    for tag in tags:
        try:
            tmp = {}
            tmp['name'] = tag.slug
            kwargs = {'tag': tag.slug,}
            if len(tmp['name']) > 0:                    
                tmp['url'] = reverse('blogging:tagged-posts',kwargs=kwargs)
                tag_list.append(tmp)
            else:
                continue
        except:
            print "Unexpected error:", sys.exc_info()[0]
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname,lineno,fn,text = frame
                print "Error in %s on line %d" % (fname, lineno)
    return tag_list

@register.assignment_tag
def get_section_children(section):
    return BlogContent.published.filter(section=section)

@register.simple_tag
def get_section_articles_count(section):
    if section:
        if section.is_leaf_node():
            posts = BlogContent.published.filter(section=section).count()
        else:
            parent_list = section.get_descendants()
            posts = BlogContent.published.filter(section__in=parent_list).count()
    else:
        posts = BlogContent.published.all().count()
    return posts

@register.assignment_tag
def get_recent_articles():
    return BlogContent.published.all()[:3]

@register.filter('has_group')
def has_group(user,groups):
    if user.is_authenticated():       
        group_list = [s for s in groups.split(',')]     
        if user.is_authenticated():
            if bool(user.groups.filter(name__in=group_list)) | user.is_superuser:
                return True
        return False

@register.filter
def selected_fields(form, field):
    print [form[field].value()]
    return [(value,label,) for value, label in form.fields[field].choices if value in form[field].value()]



register.tag(ContentRender)
register.tag(ContactTag)
register.tag(DraftTag)
register.tag(PublishedTag)
register.tag(PendingTag)
register.tag(ReviewTag)
