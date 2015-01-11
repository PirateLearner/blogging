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
class Article(models.Model):
	Body = models.TextField()
	Tagline = models.CharField(max_length=100)
	title = models.CharField(max_length=100)
	pid_count = models.IntegerField()
	Summary = models.TextField()
	tag_list = [  { 'name':'Body_tag' , 'type' :'TextField'} , { 'name':'Tagline_tag' , 'type' :'CharField'} , { 'name':'title_tag' , 'type' :'CharField'} , { 'name':'pid_count_tag' , 'type' :'IntegerField'} , { 'name':'Summary_tag' , 'type' :'TextField'} ,]

	def __str__(self):
		return "Article"

	def render_to_template(self,db_object):
		for tag_name in self.tag_list:
			current_field = tag_lib.get_field_name_from_tag(str(tag_name['name']))
			result_field = tag_lib.parse_content(db_object,tag_name)
			if current_field == 'Body' : 
				self.Body = result_field 

			if current_field == 'Tagline' : 
				self.Tagline = result_field 

			if current_field == 'title' : 
				self.title = result_field 

			if current_field == 'pid_count' : 
				self.pid_count = int(result_field) 

			if current_field == 'Summary' : 
				self.Summary = result_field 

	def render_to_db(self,db_object):
		temp_data = ""
		for tag_name in self.tag_list:
			current_field = tag_lib.get_field_name_from_tag(str(tag_name['name']))
			tag_start = "%% " + str(tag_name["name"]) + " %% " 
			tag_end = "%% endtag " + str(tag_name["name"]) + " %%"
			if current_field == 'Body' : 
				temp_dict = tag_lib.insert_tag_id(self.Body, self.pid_count)
				self.Body = str(temp_dict['content'])
				self.pid_count = int(temp_dict['pid_count'])
				tagged_field = tag_start + self.Body + tag_end 
				temp_data += tagged_field 

			if current_field == 'Tagline' : 
				temp_dict = tag_lib.insert_tag_id(self.Tagline, self.pid_count)
				self.Tagline = str(temp_dict['content'])
				self.pid_count = int(temp_dict['pid_count'])
				tagged_field = tag_start + self.Tagline + tag_end 
				temp_data += tagged_field 

			if current_field == 'title' : 
				tagged_field = tag_start + self.title + tag_end 
				db_object.title = self.title 

			if current_field == 'Summary' : 
				temp_dict = tag_lib.insert_tag_id(self.Summary, self.pid_count)
				self.Summary = str(temp_dict['content'])
				self.pid_count = int(temp_dict['pid_count'])
				tagged_field = tag_start + self.Summary + tag_end 
				temp_data += tagged_field 

		tagged_field = ' %% pid_count_tag %% ' + str(self.pid_count) + '%% endtag pid_count_tag %%'
		temp_data += tagged_field
		db_object.data = temp_data

class ArticleForm(forms.ModelForm):
	Body =  forms.CharField(widget = CKEditorWidget())
	Tagline =  forms.CharField()
	Summary =  forms.CharField(widget = CKEditorWidget())
	section = forms.ModelChoiceField(
queryset=BlogParent.objects.all().filter(~Q(title="Orphan"),~Q(title="Blog"),children=None,),
empty_label=None,
required = True,
label = "Select Parent")
	tags = TagField(help_text= "comma seperated fields for tags")
	class Meta:
		model = Article
		exclude=('pid_count',)
	def save(self):
		instance = Article()
		instance.Body = self.cleaned_data["Body"]
		instance.Tagline = self.cleaned_data["Tagline"]
		instance.title = self.cleaned_data["title"]
		instance.Summary = self.cleaned_data["Summary"]
		return instance
