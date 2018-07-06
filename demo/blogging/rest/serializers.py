'''
Created on 15-Mar-2018

@author: anshul
'''

from blogging.models import Content
from blogging.settings import blog_settings

if blog_settings.USE_POLICY:
    from blogging.models import Policy

if blog_settings.USE_TEMPLATES:
    from blogging.models import Template
    
from rest_framework import serializers

from django.contrib.auth.models import User
from rest_framework.serializers import (HyperlinkedRelatedField,CharField)

from django.db import transaction

from django.utils import timezone


if blog_settings.USE_TEMPLATES:
    class TemplateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Template
            fields = ('id', 'name', 'fields', 'author')
            extra_kwargs = {
                                'author': {'required': False},
                            }
            
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
            if super(serializers.ModelSerializer, self).is_valid(self):
                import json
                try:
                    json.loads(self.validated_data.get('fields'))
                except:
                    self.errors['detail'] = "malformed JSON"
                    return False
                if self.instance is None:
                    from blogging.factory import CreateTemplate as T
                    if( T.file_exists(self.validated_data.get('name'))):
                        print('File exists')
                        self.errors['detail'] = "File already exists"
                        return False
                return True
            return False

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    author = HyperlinkedRelatedField(queryset=User.objects.all(), 
                                     view_name='user-detail',
                                     required = False)
    text = CharField(style={'base_template': 'textarea.html'}, required=False)
    class Meta:
        model = Content
        #fields = ('url', 'id', 'title', 'text', 'author', 
        #          'create_date', 'last_modified')
        exclude = ('is_active',)
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
                   and self._validated_data.get('text', None) is None) or \
                   (self._validated_data.get('title',None) is not None \
                   and self._validated_data.get('text', None) is not None and \
                   len(self._validated_data.get('title').strip()) == 0 and \
                   len(self._validated_data.get('text').strip()) == 0):
                    self.errors['detail'] = ['Either title or content must be non-empty']
                    return False
                return True
            else:
                #It is possible that we are partially updating stuff. So, both 
                # fields may not be updated. But text must not be empty if they
                # are non-empty
                if (self._validated_data.get('title',None) is not None \
                   and self._validated_data.get('text', None) is not None and \
                   len(self._validated_data.get('title').strip()) == 0 and \
                   len(self._validated_data.get('text').strip()) == 0):
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
        #policy = serializers.PrimaryKeyRelatedField(queryset = Policy.objects.all(),
        #                                            many = True)
        template = serializers.PrimaryKeyRelatedField(queryset = 
                                                      Template.objects.all(),
                                                      required = False)
        class Meta:
            model = Content
            exclude = ('is_active',)
            extra_kwargs = {'url': {'view_name':'content/manage-detail'},
                            'title': {'max_length': 100,
                                      'required': False},
                            'policy': {'required': False},
                            }

        def create(self, validated_data):
            policy_data = validated_data.pop('policy', None)
            with transaction.atomic():
                entry = Content.objects.create(**validated_data)
                for policy in policy_data:
                    entry.policy.create(**policy)
                    #Policy.objects.create(entry=entry, **policy)
                if len(policy_data) == 0:
                    entry.policy.create(policy='PUB')
                    #Policy.objects.create(entry=entry, policy='PUB')
            return entry
        
        def update(self, instance, validated_data):
            policy_data = validated_data.pop('policy', None)

            instance.title = validated_data.get('title', instance.title)
            instance.text = validated_data.get('text', instance.text)
            with transaction.atomic():
                instance.save()
                for policy_entry in policy_data:
                    policy = instance.policy.get(policy=policy_entry.get('policy'))
                    policy.start = policy_entry.get('start', policy.start)
                    policy.end = policy_entry.get('end', policy.end)
                    policy.save()
            return instance
        
        def is_valid(self):
            if super().is_valid() is False:
                return False
            if self.instance is not None and \
                self.validated_data.get('template', None) is not None:
                if self.instance.id != \
                        self.validated_data.get('template').id:
                    return False
            return True
                
else:
    class ManageSerializer(ContentSerializer):
        class Meta:
            model = Content
            fields = ('url','id', 'title', 'text', 'author', 'create_date', 
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
        object_ids = validated_data.get('objects')
        action = validated_data.get('action')
        
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
        
