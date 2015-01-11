from django.db import models
from blogging.models import *
from django import forms
from blogging.forms import *
from ckeditor.widgets import CKEditorWidget
from taggit.forms import * 
from django.db.models import Q 
from mptt.forms import TreeNodeChoiceField 
"""
This is auto generated script file.
It defined the wrapper class for specified content type.
"""
class DefaultSection(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    tag_list = [ { 'name':'title_tag' , 'type' :'CharField'}, { 'name':'content_tag' , 'type' :'TextField'}  ,]

    def __init__(self):
        self.title = " "
        self.content = " "
    def __str__(self):
        return "DefaultSection"

    def render_to_template(self,db_object):
        self.title = db_object.title 
        self.content = db_object.data 

    def render_to_db(self,db_object):
        print "inside the render to DB function: "
        db_object.title = self.title
        db_object.data = self.content

class DefaultSectionForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    parent = TreeNodeChoiceField(queryset=BlogParent.objects.all().filter(~Q(title="Orphan"),~Q(title="Blog")),required=True, label = "Select Parent" )
    class Meta:
        model = DefaultSection
    def save(self):
        instance = DefaultSection()
        instance.title = self.cleaned_data["title"]
        instance.Preface = self.cleaned_data["Preface"]
        instance.Summary = self.cleaned_data["Summary"]
        return instance

        
