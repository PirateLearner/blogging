'''
Created on 21-Mar-2018

@author: anshul
'''
from django import forms
from blogging.models import Content

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
