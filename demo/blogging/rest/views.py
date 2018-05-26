'''
Created on 15-Mar-2018

@author: anshul
'''

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from blogging.settings import blog_settings

from blogging.models import Content

if blog_settings.USE_POLICY:
    from blogging.models import Policy
if blog_settings.USE_TEMPLATES:
    from blogging.models import Template
from blogging.rest.serializers import (ContentSerializer, ManageSerializer, 
                                       BulkAction, TemplateSerializer)

from django.http import Http404

from rest_framework.decorators import (list_route, 
                                       detail_route)

from blogging.rest.permissions import IsAdminOrAuthor
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django.db.models import Q
from django.utils import timezone

from blogging.factory import CreateTemplate
from importlib import import_module

class ContentView(viewsets.ViewSet):
    http_method_names = ['get', 'head']
    
    def get_queryset(self):
        username = self.request.query_params.get('author', None)
        pin = self.request.query_params.get('pins', None)
        if pin is not None:
            queryset = Content.objects.get_pinned(publish_filter=True).order_by('-create_date')
        else:
            queryset = Content.objects.get_published()

        if username is not None:
            queryset = queryset.filter(author__username=username)
            
        return queryset
    
    def list(self, request, format=None):
        queryset = self.get_queryset()
        serializer = ContentSerializer(queryset, 
                                       many=True, 
                                       context={'request':request})
        return Response(serializer.data)
    
    def get_object(self, pk):
        try:
            if not blog_settings.USE_POLICY:
                return Content.objects.filter(id=pk).filter(is_active=True) 
            
            return Content.objects.filter(id = pk).filter(Q(policy__policy=
                                Policy.PUBLISH)& Q(policy__start__lte=
                                timezone.now()) & (Q(policy__end__gt=
                                timezone.now()) | Q(policy__end__isnull=True)))[0]
        except:
            raise Http404
        
    def retrieve(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ContentSerializer(instance=obj, 
                                       context={'request':request})
        return Response(serializer.data)
    
class ManageView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        username = self.request.query_params.get('author', None)
        draft_only = self.request.query_params.get('drafts', None)
        publish_only = self.request.query_params.get('published', None)
        pin = self.request.query_params.get('pins', None)
        
        if draft_only is not None and publish_only is not None:
            #Both are set, that implies get all
            draft_only = None
            publish_only = None
            
        filtermap = {'author': Q(author__username=username),
                     'draft' : Q(policy__policy=Policy.PUBLISH) & 
                               ( Q(policy__start__isnull=True) | 
                                 Q(policy__start__gt= timezone.now()) |
                                 (  Q(policy__start__lte=timezone.now()) & 
                                    Q(policy__end__lt=timezone.now())
                                  )
                                ),
                     'published':(Q(policy__policy=
                                Policy.PUBLISH)& Q(policy__start__lte=
                                timezone.now()) & (Q(policy__end__gt=
                                timezone.now()) | Q(policy__end__isnull=True))),
                     'pinned': (Q(policy__policy=
                                Policy.PIN)& Q(policy__start__lte=
                                timezone.now()) & (Q(policy__end__gt=
                                timezone.now()) | Q(policy__end__isnull=True)))}
        
        queryset = Content.objects.all().order_by('-create_date')
        
        if username is not None:
            queryset = queryset.filter(filtermap['author'])
        if pin is not None:
            queryset = queryset.filter(filtermap['pinned'])
        if draft_only is not None:
            queryset = queryset.filter(filtermap['draft'])
        elif publish_only is not None:
            queryset = queryset.filter(filtermap['published'])
            
        return queryset
    
    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [permission() for permission in [IsAdminOrAuthor]]
        else:
            permission_classes = viewsets.ViewSet.get_permissions(self)
        return permission_classes
    
    def list(self, request, format=None):
        serializer = ManageSerializer(self.get_queryset(), 
                                       many=True, 
                                       context={'request':request})
        return Response(serializer.data)
    
    @list_route(['post'])
    def action(self, request, format=None):
        serializer = BulkAction(data = request.data,
                                context={'request':request})
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, format=None):
        template_id = request.data.get('template', None)
        if template_id is not None:
            try:
                template = Template.objects.get(id=template_id).name
                serializer_name = CreateTemplate.get_manage_serializer_name(template)
                
                module = import_module('blogging.custom.'+\
                            CreateTemplate.get_file_name(template))
                serializer_obj = getattr(module, serializer_name)
                serializer = serializer_obj(data=request.data, 
                                       context={'request':request})
            except:
                return Response({'detail': "Template not found"}, 
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = ManageSerializer(data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return Content.objects.get(pk = pk)
        except Content.DoesNotExist:
            raise Http404
        
    def retrieve(self, request, pk, format=None):
        obj = self.get_object(pk)
        
        try:
            template = obj.mapped.name
            serializer_name = CreateTemplate.get_manage_serializer_name(template)
            module = import_module(template)
            serializer_obj = getattr(module, serializer_name)
            serializer = serializer_obj(data=request.data, 
                                       context={'request':request})
        except:
            serializer = ManageSerializer(instance=obj, 
                                       context={'request':request})
        return Response(serializer.data)
        
    def update(self, request, pk, format=None):
        obj = self.get_object(pk)
        try:
            template = obj.mapped.name
            serializer_name = CreateTemplate.get_manage_serializer_name(template)
            module = import_module(template)
            serializer_obj = getattr(module, serializer_name)
            serializer = serializer_obj(instance=obj,
                                        data=request.data, 
                                       context={'request':request})
        except:        
            serializer = ManageSerializer(instance=obj, data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk, format=None):
        return self.update(request, pk, format)
    
    def partial_update(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ManageSerializer(instance=obj, data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    @detail_route(['post', 'put', 'patch', 'delete'])
    def publish(self, request, pk, format=None):
        pass
    
class TemplateView(viewsets.ModelViewSet):
    serializer_class = TemplateSerializer
    queryset = Template.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def create(self, request, format=None):
        from blogging.factory import CreateTemplate
        import json
        serializer = TemplateSerializer(data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            #Create custom template class
            template = CreateTemplate(name=serializer.validated_data.get('name'),
                                      members = json.loads(serializer.validated_data.get('fields')))
            template.save()
            serializer.save(author = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = TemplateSerializer(instance=obj, data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    