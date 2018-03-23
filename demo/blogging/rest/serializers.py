'''
Created on 15-Mar-2018

@author: anshul
'''

from blogging.models import Content
from rest_framework import serializers

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Content
        fields = ('url', 'id', 'title', 'data', 'author', 
                  'create_date', 'last_modified')