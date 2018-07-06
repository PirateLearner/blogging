'''
Created on 21-Mar-2018

@author: anshul
'''
from django import forms
from blogging.models import Content
from blogging.settings import blog_settings

if blog_settings.USE_POLICY:
    from blogging.models import Policy

if blog_settings.USE_TEMPLATES:
    from blogging.models import Template

class ContentForm(forms.ModelForm):
    title = forms.CharField(required = False)
    text = forms.CharField(required = False, widget=forms.Textarea)
    
    class Meta:
        model = Content
        fields = ['title', 'text',]
        if blog_settings.USE_TEMPLATES is True:
            fields += ['template',]
        
    def is_valid(self):
        if (forms.ModelForm.is_valid(self)):
            if len(self.cleaned_data['title']) is 0 and len(self.cleaned_data['text']) is 0:
                self.errors['title'] = ['Either title or content must be non-empty']
                return False
            return True
        return False

if blog_settings.USE_POLICY:
    class PolicyForm(forms.ModelForm):
        class Meta:
            model = Policy
            fields = ('id', 'entry', 'policy', 'start', 'end')
        
    class ManageForm(ContentForm):
        policy = PolicyForm()
        class Meta:
            model = Content
            exclude = ('is_active',)
            
if blog_settings.USE_TEMPLATES:
    class TemplateForm(forms.ModelForm):
        class Meta:
            model = Template
            exclude = ('author',)
        
        def is_valid(self):
            '''
            Validate the JSON is well formed.
            Validate that the eventual filename that will be created does not 
            already exist, and if it is an update, then it already exists. 
            (How will we do that?):
            - Have a field 'raw_name' in the file that contains the original
              name that the user had asked for. If it is the same, then we are
              updating.
            '''
            if super(forms.ModelForm, self).is_valid():
                import json
                try:
                    json.loads(self.cleaned_data.get('fields'))
                except:
                    self.errors['detail'] = "malformed JSON"
                    return False
                if self.instance.id is None:
                    from blogging.factory import CreateTemplate as T
                    if( T.file_exists(self.cleaned_data.get('name'))):
                        self.errors['detail'] = ":File already exists"
                        return False
                    return True
                return True
            return False