from blogging import tag_lib
from django.db import models
from blogging.models import *
from django import forms
from blogging.forms import *
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
import json
from django.db.models import Q 
from mptt.forms import TreeNodeChoiceField
"""
This is auto generated script file.
It defined the wrapper class for specified content type.
"""

class DefaultsectionForm(forms.Form):
    title = forms.CharField(max_length = 100)
    pid_count = forms.IntegerField(required=False)
    parent = TreeNodeChoiceField(queryset=BlogParent.objects.all().filter(~Q(title="Orphan"),~Q(title="Blog")),required=True,empty_label=None, label = "Select Parent" )

    content =  forms.CharField(widget = CKEditorUploadingWidget(config_name='author'))
    def __init__(self,action, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
        	json_data = json.loads(instance.data)
                kwargs.update(initial={
                        # 'field': 'value'
                        'title': instance.title,
                        'parent': instance.parent,
                        'content': json_data['content'],
                        'pid_count': json_data['pid_count'],
                })
        super(DefaultsectionForm, self).__init__(*args, **kwargs)

    def save(self,post,commit=False):
        post.pop('parent')
        post.pop('title')
        post.pop('csrfmiddlewaretoken')
        post.pop('submit')
        
        if commit == False:
            return json.dumps(post.dict())

        for k,v in post.iteritems():
            if str(k) != 'pid_count' :
                tmp = {}
                tmp = tag_lib.insert_tag_id(str(v),self.cleaned_data["pid_count"])
                post[k] = tmp['content'] 
                post['pid_count'] = tmp['pid_count']
                print "printing post values ", post[k], "pid count ", post['pid_count'] 
            
        print json.dumps(post)
        return json.dumps(post)
     
