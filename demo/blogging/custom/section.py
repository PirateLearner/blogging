from blogging import tag_lib
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
class Section(models.Model):
	Body = models.TextField()
	title = models.CharField(max_length=100)
	tag_list = [  { 'name':'Body_tag' , 'type' :'TextField'} , { 'name':'title_tag' , 'type' :'CharField'} ,]

	def __str__(self):
		return "Section"

	def render_to_template(self,db_object):
		for tag_name in self.tag_list:
			current_field = tag_lib.get_field_name_from_tag(str(tag_name['name']))
			result_field = tag_lib.parse_content(db_object,tag_name)
			if current_field == 'Body' : 
				self.Body = result_field 

			if current_field == 'title' : 
				self.title = result_field 

	def render_to_db(self,db_object):
		temp_data = ""
		for tag_name in self.tag_list:
			current_field = tag_lib.get_field_name_from_tag(str(tag_name['name']))
			tag_start = "%% " + str(tag_name["name"]) + " %% " 
			tag_end = "%% endtag " + str(tag_name["name"]) + " %%"
			if current_field == 'Body' : 
				tagged_field = tag_start + self.Body + tag_end 
				temp_data += tagged_field 

			if current_field == 'title' : 
				tagged_field = tag_start + self.title + tag_end 
				db_object.title = self.title 

		db_object.data = temp_data

class SectionForm(forms.ModelForm):
	Body =  forms.CharField(widget = CKEditorWidget())
	parent = TreeNodeChoiceField(queryset=BlogParent.objects.all().filter(~Q(title="Orphan"),~Q(title="Blog")),required=False,empty_label=None, label = "Select Parent" )
	class Meta:
		model = Section
	def save(self):
		instance = Section()
		instance.Body = self.cleaned_data["Body"]
		instance.title = self.cleaned_data["title"]
		return instance
