from django import forms

from django.conf import settings

from django.contrib.admin import widgets
from blogging.models import *
import django_select2
import taggit
from blogging.widgets import SelectWithPopUp
from django.db import models
from ckeditor.widgets import CKEditorWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit

CUSTOM_FIELD_TYPE = (
	('CharField', 'TextField'),
	('TextField', 'TextArea'),
#	('ImageField', 'Image'),
#	('FileField', 'File Upload'),
#	('IntegerField', 'Number'),
)

CONTACT_TYPE = (
			('Queries','Make a Query!'),
			('FeedBack','Give Your Feedback!'),
			('Feature','Suggest A Feature!'),
			('Join','Join Us!'),
			)

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

class PostTagWidget(django_select2.widgets.Select2Mixin, taggit.forms.TagWidget):
    def __init__(self, *args, **kwargs):
        options = kwargs.get('select2_options', {})
        options['tags'] = list(taggit.models.Tag.objects.values_list('name', flat=True))
        options['tokenSeparators'] = [',', ]
        kwargs['select2_options'] = options
        super(PostTagWidget, self).__init__(*args, **kwargs)

    def render_js_code(self, *args, **kwargs):
        js_code = super(PostTagWidget, self).render_js_code(*args, **kwargs)
        return js_code.replace('$', 'jQuery')


class PostForm(forms.ModelForm):

	data = forms.CharField(label="Data Field", widget=CKEditorWidget())
	class Meta:
		widgets = {'tags': PostTagWidget, }
		model = BlogContent

class ParentForm(forms.ModelForm):

	data = forms.CharField(label="Data Field", widget=CKEditorWidget(), help_text=('Please Upload at least one picture for preview!!!'))
	class Meta:
		model = BlogParent


class ContentTypeForm(forms.Form):
	ContentType = forms.ModelChoiceField(
					queryset=BlogContentType.objects.all(),
					empty_label=None,
					required = True,
					label = "Select Content type or Create New!",
					widget=SelectWithPopUp)
	def __init__(self, *args, **kwargs):
		super(ContentTypeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		
		self.helper.form_id = 'id-ContentTypeForm'
#		self.helper.form_class = 'blueForms'
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
#		self.helper.form_action = reverse('blogging:contact-us')
		self.helper.layout = Layout(
				Fieldset(
                'You can select the existing Content Type or Create New for your Post.',
                'ContentType',
            ),
			
            ButtonHolder(
                Submit('submit', 'next', css_class='button white'),
                Submit('submit', 'delete', css_class='btn-danger')
                
            ),
			
			)


class ContentTypeCreationForm(forms.ModelForm):

	helper1 = FormHelper()

	def __init__(self, *args, **kwargs):
		
		super(ContentTypeCreationForm, self).__init__(*args, **kwargs)
		
		self.helper1.form_id = 'id-ContentTypeCreationForm'
		#		self.helper.form_class = 'blueForms'
		self.helper1.form_class = 'form-inline'
		self.helper1.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper1.form_tag = False
#		self.helper1.template = 'blogging/inline_field.html'

	class Meta:
		model = BlogContentType

class FieldTypeForm(forms.Form):
	field_name = forms.CharField()
	field_type = forms.ChoiceField(widget = forms.Select(),choices=CUSTOM_FIELD_TYPE)
	

	
class FormsetHelper(FormHelper):
	def __init__(self, *args, **kwargs):
		super(FormsetHelper, self).__init__(*args, **kwargs)
		
		self.form_id = 'id-FieldTypeForm'
#		self.helper.form_class = 'blueForms'
		self.form_class = 'form-inline'
		self.field_template = 'blogging/inline_field.html'
		self.form_method = 'post'
		self.form_tag = False
#		self.template = 'blogging/table_inline_formset.html'
		self.layout = Layout(
                'field_name',
                'field_type',
			)
	
class ContentForm(forms.ModelForm):
	class Meta:
		model = BlogContent

class PostEditForm(forms.ModelForm):

	class Meta:
	    model = BlogContent
	    widgets = {'tags': PostTagWidget,
		   'publication_start': widgets.AdminSplitDateTime }
	    exclude = (
	        'page',
	        'create_date',
	        'author_id',
	        'special_flag',
	        'published_flag',
	    'last_modefied',
	    'url_path',
	    'objects',
	    'slug',
	    )

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
									widget = forms.Select(),choices=CONTACT_TYPE)
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
		self.helper = FormHelper()
		
		self.helper.form_id = 'id-ContactForm'
#		self.helper.form_class = 'blueForms'
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
#		self.helper.form_action = reverse('blogging:contact-us')
		self.helper.layout = Layout(
				Fieldset(
                'Queries, Questions, Suggestions, Feedback or for giving a pat on our back, please feel free to contact Us',
                'contact_type',
                'name',
                'email',
                'content',
                'extra',
				Field('honeypot', type="hidden"),
            ),
			
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            ),
			
			)
#		self.helper.add_input(Submit('submit', 'Submit'))

