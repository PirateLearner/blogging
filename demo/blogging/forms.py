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
        fields = ['title', 'text']
        
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
            fields = '__all__'