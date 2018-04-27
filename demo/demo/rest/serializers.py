'''
Created on 15-Mar-2018

@author: anshul

@brief All serializers that do not belong to a specific app but must exist to 
support that app reside here. For example, a User serializer is required for
the blogging app, but the blogging app does not create or manage users. So, the
user serializer is implemented here.
'''
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="user-detail")
    gravatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email', 'is_staff', 'gravatar')
        
    def get_gravatar(self, obj):
        return '#'