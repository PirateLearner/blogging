'''
Created on 21-Mar-2018

@author: anshul
'''
from django import forms
from blogging.models import Content

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'data', 'author']