'''
Created on 15-Mar-2018

@author: anshul
'''

from blogging.models import Content, Policy
from rest_framework import serializers

from django.contrib.auth.models import User
from rest_framework.serializers import (HyperlinkedRelatedField,CharField)
from blogging.settings import blog_settings
from django.db import transaction

from django.utils import timezone

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    author = HyperlinkedRelatedField(queryset=User.objects.all(), 
                                     view_name='user-detail',
                                     required = False)
    data = CharField(style={'base_template': 'textarea.html'}, required=False)
    class Meta:
        model = Content
        fields = ('url', 'id', 'title', 'data', 'author', 
                  'create_date', 'last_modified')
        extra_kwargs = {'title': {'max_length': 100,
                                  'required': False},
                        }

    def is_valid(self):
        if (serializers.HyperlinkedModelSerializer.is_valid(self)):
            #If some field is not posted, it is missing in the dictionary
            #Unlike forms where it is empty
            #Perform this check only on new creations
            if self.instance is None:
                if (self._validated_data.get('title',None) is None \
                   and self._validated_data.get('data', None) is None) or \
                   (self._validated_data.get('title',None) is not None \
                   and self._validated_data.get('data', None) is not None and \
                   len(self._validated_data.get('title').strip()) == 0 and \
                   len(self._validated_data.get('data').strip()) == 0):
                    self.errors['detail'] = ['Either title or content must be non-empty']
                    return False
                return True
            else:
                #It is possible that we are partially updating stuff. So, both 
                # fields may not be updated. But text must not be empty if they
                # are non-empty
                if (self._validated_data.get('title',None) is not None \
                   and self._validated_data.get('data', None) is not None and \
                   len(self._validated_data.get('title').strip()) == 0 and \
                   len(self._validated_data.get('data').strip()) == 0):
                    self.errors['detail'] = ['Either title or content must be non-empty']
                    return False
                return True
        return False

if blog_settings.USE_POLICY:
    class PolicySerializer(serializers.ModelSerializer):
        class Meta:
            model = Policy
            fields = ('id', 'entry', 'policy', 'start', 'end')
            extra_kwargs = {'start': {'required': False},
                            'end': {'required': False},
                            'entry': {'required': False}}
    
    class ManageSerializer(ContentSerializer):
        policy = PolicySerializer(many=True)
        
        class Meta:
            model = Content
            fields = ('url', 'id', 'title', 'data', 'author', 'create_date', 
                      'last_modified', 'policy')
            extra_kwargs = {'url': {'view_name':'content/manage-detail'},
                            'title': {'max_length': 100,
                                      'required': False},
                            }
            
        def create(self, validated_data):
            policy_data = validated_data.pop('policy')
            with transaction.atomic():
                entry = Content.objects.create(**validated_data)
                for policy in policy_data:
                    Policy.objects.create(entry=entry, **policy)
            return entry
        
        def update(self, instance, validated_data):
            policy_data = validated_data.pop('policy')
            instance.title = validated_data.get('title', instance.title)
            instance.data = validated_data.get('data', instance.data)
            with transaction.atomic():
                instance.save()
                for policy_entry in policy_data:
                    policy = instance.policy.get(policy=policy_entry.get('policy'))
                    policy.start = policy_entry.get('start', policy.start)
                    policy.end = policy_entry.get('end', policy.end)
                    policy.save()
            return instance
else:
    class ManageSerializer(ContentSerializer):
        class Meta:
            model = Content
            fields = ('url','id', 'title', 'data', 'author', 'create_date', 
                      'last_modified', 'is_active')
            extra_kwargs = {'url': {'view_name':'content/manage-detail'}}
            
class BulkAction(serializers.Serializer):
    #Cannot have bulk schedules. That is, it's either ON or OFF
    objects = serializers.ListField(child=serializers.IntegerField(min_value = 1))
    action  = serializers.ChoiceField([('PUBL', 'Publish'),
                                       ('UNPB', 'Unpublish'),
                                       ('PIN', 'Pin'),
                                       ('UPIN', 'Unpin'),
                                       ('DEL', 'Delete')])
    
    def create(self, validated_data):
        object_ids = self.validated_data.get('objects')
        action = self.validated_data.get('action')
        
        if action is 'PUBL' or 'UNPB':
            action_method = Policy.PUBLISH
        elif action is 'PIN' or 'UPIN':
            action_method = Policy.PIN
        
        with transaction.atomic():
            objects = Content.objects.filter(id__in = object_ids)
            for object in objects:
                (policy, created) = object.policy.get_or_create(entry=object, 
                                                      policy=action_method)
                if action is 'UNPB'and policy.is_published():
                    policy.end = timezone.now()
                    policy.save()
                elif action is 'PUBL' and not policy.is_published():
                    policy.start = timezone.now()
                    if policy.end is not None and policy.end <= timezone.now():
                        policy.end = None
                    policy.save()
                elif action is 'UPIN' and policy.is_pinned():
                    policy.end = timezone.now()
                    policy.save()
                elif action is 'PIN' and not policy.is_pinned():
                    policy.start = timezone.now()
                    if policy.end is not None and policy.end <= timezone.now():
                        policy.end = None
                    policy.save()
                elif action is 'DEL':
                    object.delete()
            return {'objects': object_ids,
                    'action' : action}
        return {'objects': object_ids,
                'action' : action}
        