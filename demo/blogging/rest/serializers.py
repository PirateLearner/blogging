'''
Created on 15-Mar-2018

@author: anshul
'''

from blogging.models import Content
from rest_framework import serializers

from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedRelatedField,CharField

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    author = HyperlinkedRelatedField(queryset=User.objects.all(), 
                                     view_name='user-detail',
                                     required = False)
    title = CharField(max_length=100, required=False)
    data = CharField(style={'base_template': 'textarea.html'}, required=False)
    class Meta:
        model = Content
        fields = ('url', 'id', 'title', 'data', 'author', 
                  'create_date', 'last_modified')
        
    def is_valid(self):
        if (serializers.HyperlinkedModelSerializer.is_valid(self)):
            #If some field is not posted, it is missing in the dictionary
            #Unlike forms where it is empty
            if self._validated_data.get('title',None) is None \
               and self._validated_data.get('data', None) is None:
                self.errors['detail'] = ['Either title or content must be non-empty']
                return False
            return True
        return False