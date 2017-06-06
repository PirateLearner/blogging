from django import forms

from django.conf import settings

from django.contrib.admin import widgets
from blogging.models import *
from taggit.models import Tag
from blogging.widgets import SelectWithPopUp
from django.db import models
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text, smart_text
import json
from blogging import tag_lib
from blogging.utils import slugify_name
from django.forms.models import  ModelChoiceField, ModelMultipleChoiceField


CUSTOM_FIELD_TYPE = (
	('CharField', 'TextField'),
	('TextField', 'TextArea'),
#	('ImageField', 'Image'),
#	('FileField', 'File Upload'),
#	('IntegerField', 'Number'),
)

CONTACT_TYPE = (
			('Queries','have a question.'),
			('FeedBack','have feedback on the site.'),
			('Feature','want to suggest a feature.'),
			('Join','want to Join.'),
			)

class Select2ChoiceField(ModelMultipleChoiceField):
    '''
    In case you are populating the fields using ajax request then 'to_python' must be 
    overridden, as default queryset is None and this function originally check if 
    returned value is in the queryset which in turns raise validation error "invalid_choice".
    '''
                
    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            #MODIFIED HERE: check for value in all object instead of self.queryset
            value = self.queryset.model.objects.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

class TagField(forms.MultipleChoiceField):

	def __init__(self, *args, **kwargs):
		super(forms.MultipleChoiceField, self).__init__(choices = [ (x.id,x.name) for x in Tag.objects.all()], *args, **kwargs)

	def to_python(self, value):
		if not value:
			return []
		return list(self._check_values(value))
	
	def _check_values(self, value):
		"""
		Given a list of possible PK values, returns a QuerySet of the
		corresponding objects. Raises a ValidationError if a given value is
		invalid (not a valid PK, not in the queryset, etc.)
		"""
		key = 'pk'
		# deduplicate given values to avoid creating many querysets or
		# requiring the database backend deduplicate efficiently.
		try:
			value = frozenset(value)
		except TypeError:
			# list of lists isn't hashable, for example
			raise ValidationError(
				self.error_messages['list'],
				code='list',
			)
		for pk in value:
			try:
				Tag.objects.filter(**{key: pk})
			except (ValueError, TypeError):
				raise ValidationError(
					self.error_messages['invalid_pk_value'],
					code='invalid_pk_value',
					params={'pk': pk},
				)
		qs = Tag.objects.filter(**{'%s__in' % key: value})
		pks = set(force_text(getattr(o, key)) for o in qs)
		for val in value:
			if force_text(val) not in pks:
				raise ValidationError(
					self.error_messages['invalid_choice'],
					code='invalid_choice',
					params={'value': val},
				)
		return qs

	def valid_value(self, value):
		"Check to see if the provided value is a valid choice"
		print "LOGS: valid_value is called "
		text_value = force_text(value.id)
		for k, v in self.choices:
			if isinstance(v, (list, tuple)):
				# This is an optgroup, so look inside the group for options
				for k2, v2 in v:
					if value.id == k2 or text_value == force_text(k2):
						return True
			else:
				if value.id == k or text_value == force_text(k):
					return True
		return False
	
def validate_empty(value):
	if value :
		raise ValidationError(u'It seems you are not human!!!')

"""
class LatestEntriesForm(forms.ModelForm):

    class Meta:

        widgets = {
            'tags': django_select2.Select2MultipleWidget
        }
"""

# class PostTagWidget(django_select2.widgets.Select2Mixin, taggit.forms.TagWidget):
#     def __init__(self, *args, **kwargs):
#         options = kwargs.get('select2_options', {})
#         options['tags'] = list(taggit.models.Tag.objects.values_list('name', flat=True))
#         options['tokenSeparators'] = [',', ]
#         kwargs['select2_options'] = options
#         super(PostTagWidget, self).__init__(*args, **kwargs)
# 
#     def render_js_code(self, *args, **kwargs):
#         js_code = super(PostTagWidget, self).render_js_code(*args, **kwargs)
#         return js_code.replace('$', 'jQuery')
# 
# 
# class PostForm(forms.ModelForm):
# 
# 	data = forms.CharField(label="Data Field", widget=CKEditorWidget())
# 	class Meta:
# 		widgets = {'tags': PostTagWidget, }
# 		model = BlogContent

class ParentForm(forms.ModelForm):

	data = forms.CharField(label="Data Field", widget=CKEditorWidget(), help_text=('Please Upload at least one picture for preview!!!'))
	class Meta:
		model = BlogParent
		exclude = ('slug',)
		

class ContentTypeForm(forms.Form):
	ContentType = forms.ModelChoiceField(
					queryset=BlogContentType.objects.all(),
					empty_label=None,
					required = True,
					label = "Select Content type or Create New!",
					widget=SelectWithPopUp)
	def __init__(self, *args, **kwargs):
		super(ContentTypeForm, self).__init__(*args, **kwargs)
# 		self.helper = FormHelper()
# 		
# 		self.helper.form_id = 'id-ContentTypeForm'
# #		self.helper.form_class = 'blueForms'
# 		self.helper.form_class = 'form-horizontal'
# 		self.helper.label_class = 'col-lg-2'
# 		self.helper.field_class = 'col-lg-8'
# 		self.helper.form_method = 'post'
# #		self.helper.form_action = reverse('blogging:contact-us')
# 		self.helper.layout = Layout(
# 				Fieldset(
#                 'You can select the existing Content Type or Create New for your Post.',
#                 'ContentType',
#             ),
# 			
#             ButtonHolder(
#                 Submit('submit', 'next', css_class='button white'),
#                 Submit('submit', 'delete', css_class='btn-danger')
#                 
#             ),
# 			
# 			)


class ContentTypeCreationForm(forms.ModelForm):

# 	helper1 = FormHelper()

	def __init__(self, *args, **kwargs):
		
		super(ContentTypeCreationForm, self).__init__(*args, **kwargs)
		
# 		self.helper1.form_id = 'id-ContentTypeCreationForm'
# 		#		self.helper.form_class = 'blueForms'
# 		self.helper1.form_class = 'form-inline'
# 		self.helper1.field_template = 'bootstrap3/layout/inline_field.html'
# 		self.helper1.form_tag = False
#		self.helper1.template = 'blogging/inline_field.html'


	
	class Meta:
		model = BlogContentType
		fields = ['content_type', 'is_leaf']

class FieldTypeForm(forms.Form):
	field_name = forms.CharField()
	field_type = forms.ChoiceField(widget = forms.Select(),choices=CUSTOM_FIELD_TYPE)
	
	def clean_field_name(self):
		print "LOGS: clean_field_name called"
		data = slugify_name(self.cleaned_data['field_name'])
		return data

	
# class FormsetHelper(FormHelper):
# 	def __init__(self, *args, **kwargs):
# 		super(FormsetHelper, self).__init__(*args, **kwargs)
# 		
# 		self.form_id = 'id-FieldTypeForm'
# #		self.helper.form_class = 'blueForms'
# 		self.form_class = 'form-inline'
# 		self.field_template = 'blogging/inline_field.html'
# 		self.form_method = 'post'
# 		self.form_tag = False
# #		self.template = 'blogging/table_inline_formset.html'
# 		self.layout = Layout(
#                 'field_name',
#                 'field_type',
# 			)
	
class ContentForm(forms.ModelForm):
	class Meta:
		model = BlogContent
		exclude = ('slug',)

# class PostEditForm(forms.ModelForm):
# 
# 	class Meta:
# 	    model = BlogContent
# 	    widgets = {'tags': PostTagWidget,
# 		   'publication_start': widgets.AdminSplitDateTime }
# 	    exclude = (
# 	        'page',
# 	        'create_date',
# 	        'author_id',
# 	        'special_flag',
# 	        'published_flag',
# 	    'last_modefied',
# 	    'url_path',
# 	    'objects',
# 	    'slug',
# 	    )

if 'cms' in settings.INSTALLED_APPS:
	class LatestEntriesForm(forms.ModelForm):

	    class Meta:
	        widgets = {
	            'tags': django_select2.Select2MultipleWidget
	        }
        
	class SectionPluginForm(forms.ModelForm):
		
		class Meta:
			model = SectionPlugin
		
		def __init__(self, *args, **kwargs):
			super(SectionPluginForm, self).__init__(*args, **kwargs)
			choices = [self.fields['parent_section'].choices.__iter__().next()]
			for page in self.fields['parent_section'].queryset:
				choices.append(
					(page.id, ''.join(['-' * page.level, page.__unicode__()]))
				)
			self.fields['parent_section'].choices = choices
		
class ContactForm(forms.Form):
	contact_type = forms.ChoiceField(label="Choose Type of Contact",required=True,
									widget=forms.RadioSelect,choices=CONTACT_TYPE)
	name = forms.CharField(
        label="What is your name?",
        max_length=80,
        required=True,
    )
	
	email = forms.EmailField(
			label="Your email?",
			required=True,
							)
	content = forms.CharField(widget=forms.Textarea,
				label="Want to say something?",
				required=True,
				)
	extra = forms.CharField(
						label="Leave it blank if you are Human",
						validators=[validate_empty],
						required=False)
	honeypot = forms.CharField(
							label="Not visible to you",
							required=False,
							validators=[validate_empty],
							)
	
	def __init__(self, *args, **kwargs):
		super(ContactForm, self).__init__(*args, **kwargs)
# 		self.helper = FormHelper()
# 		
# 		self.helper.form_id = 'id-ContactForm'
# #		self.helper.form_class = 'blueForms'
# 		self.helper.form_class = 'form-horizontal'
# 		self.helper.label_class = 'col-lg-2'
# 		self.helper.field_class = 'col-lg-8'
# 		self.helper.form_method = 'post'
# #		self.helper.form_action = reverse('blogging:contact-us')
# 		self.helper.layout = Layout(
# 				Fieldset(
#                 'Queries, Questions, Suggestions, Feedback or for giving a pat on our back, please feel free to contact Us',
#                 'contact_type',
#                 'name',
#                 'email',
#                 'content',
#                 'extra',
# 				Field('honeypot', type="hidden"),
#             ),
# 			
#             ButtonHolder(
#                 Submit('submit', 'Submit', css_class='button white')
#             ),
# 			
# 			)
#		self.helper.add_input(Submit('submit', 'Submit'))

# class TestFormClass(forms.Form):
# 	title = forms.CharField(max_length = 100)
# 	description = forms.CharField(widget=forms.Textarea, required=False)
# 	note = forms.CharField(widget=forms.Textarea, required=False)
# 	tags = TagField()
# 	section = forms.ModelChoiceField(queryset= BlogParent.objects.filter(children=None) , empty_label=None)
# 	pid_count = forms.IntegerField(required=False)
# 	def __init__(self, *args, **kwargs):
# 		self.helper = FormHelper()
# 		
# 		self.helper.form_id = 'id-TestFormClass'
# #		self.helper.form_class = 'blueForms'
# 		self.helper.form_class = 'form-horizontal'
# 		self.helper.label_class = 'col-lg-2'
# 		self.helper.field_class = 'col-lg-8'
# 		self.helper.form_method = 'post'
# 		self.helper.form_action = reverse('blogging:testing-view')
# 		self.helper.layout = Layout(
# 				Fieldset(
#                 'Testing the JSON FORM',
#                 'title',
#                 'description',
#                 'note',
#                 'tags',
#                 'section',
#                 Field('pid_count', type="hidden"),
#             ),
# 			
#             ButtonHolder(
#                 Submit('submit', 'Submit', css_class='button white')
#             ),
# 			
# 			)
# 		super(TestFormClass, self).__init__(*args, **kwargs)
# 
# 	
# 	def save(self,post,db_instance=None):
# 		print "LOGS: Section --> ", post.pop('section')
# 		print "LOGS: Tags --> ", post.pop('tags')
# 		print "LOGS: Tags --> ", post.pop('title')
# 		post.pop('csrfmiddlewaretoken')
# 		post.pop('submit')
# 		if db_instance != None:
# 			instance = db_instance
# 		else:
# 			instance = BlogContent()
# 		instance.title = self.cleaned_data["title"]
# 		instance.section = self.cleaned_data["section"]
# 
# 		for k,v in post.iteritems():
# 			if str(k) != 'pid_count' :
# 				tmp = {}
# 				tmp = tag_lib.insert_tag_id(str(v),self.cleaned_data["pid_count"])
# 				post[k] = tmp['content']
# 				post['pid_count'] = tmp['pid_count']
# 			
# 		json_str = json.dumps(post.dict())
# 		instance.data = str(json_str)
# 		print "LOGS: printing the json_str", json_str
# 		return instance
		

"""
class PageForm(forms.Form):
        title = forms.CharField()
	parent = forms.ModelChoiceField(queryset= BlogParent.objects.filter(children=None) , empty_label=None)
	content_type = forms.ModelChoiceField(queryset = BlogContentType.objects.all(),empty_label=None)
        body = forms.CharField( widget=TextEditorWidget(attrs = {'toolbar': 'HTMLField'}) )

        def clean_title(self):
                title = self.cleaned_data['title']
                num_words = len(title.split())
                if num_words < 4:
                    raise forms.ValidationError("Not enough words!")
                return title

        def clean_body(self):
                body = self.cleaned_data['body']
                num_words = len(body.split())
                if num_words < 4:
                    raise forms.ValidationError("Not enough words!")
                return body


"""
