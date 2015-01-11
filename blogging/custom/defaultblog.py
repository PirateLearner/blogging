from blogging import tag_lib
from django.db import models
from blogging.models import *
from django import forms
from blogging.forms import *
from ckeditor.widgets import CKEditorWidget
from taggit.forms import *
from django.db.models import Q
from mptt.forms import     TreeNodeChoiceField
"""
This is auto generated script file.
It defined the wrapper class for specified content type.
"""
class DefaultBlog(models.Model):
#    model_name = models.CharField(max_length=100)
    title = models.CharField(max_length = 100)
    content = models.TextField()
    tag_list = [  { 'name':'title_tag' , 'type' :'CharField'},{ 'name':'content_tag' , 'type' :'TextField'} ,]

    def __init__(self):
        self.title = " "
    def __str__(self):
        return "BLOG"

    def render_to_template(self,db_object):
        self.title = db_object.title 
        self.content = db_object.data 

    def render_to_db(self,db_object):
        
        print "inside the render to DB function: "
        db_object.title = self.title
        db_object.data = self.content

class DefaultBlogForm(forms.ModelForm):
    section = forms.ModelChoiceField(
                                    queryset=BlogParent.objects.all().filter(~Q(title='Orphan'),~Q(title='Blog'),children=None,),
                                    empty_label=None,
                                    required = True,
                                    label = "Select Parent")
    content = forms.CharField(widget=CKEditorWidget())
    tags = TagField(help_text= "comma seperated fields for tags")
    class Meta:
        model = DefaultBlog
    def save(self):
        instance = DefaultBlog()
        instance.title = self.cleaned_data['title']
        instance.content = self.cleaned_data['content']
        return instance
        
