import tag_lib
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
class Testing1(models.Model):
	title = models.CharField(max_length=100)
	Content = models.CharField()
	title = models.CharField()
	tag_list = [ { 'name':'title_tag' , 'type' :'CharField'},  { 'name':'Content_tag' , 'type' :'CharField'} , { 'name':'title_tag' , 'type' :'CharField'} ,]

	def __init__(self):
		self.Content = " "
		self.title = " "
	def __str__(self):
		return "Testing1"

	def render_to_template(self,db_object):
		for tag_name in self.tag_list:
			current_field = tag_lib.get_field_name_from_tag(str(tag_name['name']))
			result_field = tag_lib.parse_content(db_object,tag_name)
			if current_field == 'Content' : 
				self.Content = result_field 

			if current_field == 'title' : 
				self.title = result_field 

	def render_to_db(self,db_object):
		for tag_name in self.tag_list:
			current_field = tag_lib.get_field_name_from_tag(str(tag_name['name']))
			tag_start = "%% " + str(tag_name["name"]) + " %% " 
			tag_end = "%% endtag " + str(tag_name["name"]) + " %%
"
			if current_field == 'Content' : 
				tagged_field = tag_start + self.Content + tag_end 
				db_object.data += tagged_field 

			if current_field == 'title' : 
				tagged_field = tag_start + self.title + tag_end 
				db_object.title = self.title 

class Testing1Form(forms.ModelForm):
	Content =  forms.CharField()
	section = forms.ModelChoiceField(
queryset=BlogParent.objects.all().filter(~Q(title="Orphan"),~Q(title="Blog"),children=None,),
empty_label=None,
required = True,
label = "Select Parent")
	tags = TagField(help_text= "comma seperated fields for tags")
	class Meta:
		model = Testing1
	def save(self):
		instance = Testing1()
		instance.Content = self.cleaned_data["Content"]
		instance.title = self.cleaned_data["title"]
		return instance
