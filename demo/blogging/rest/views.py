'''
Created on 15-Mar-2018

@author: anshul
'''

from rest_framework import viewsets, status
from rest_framework.response import Response
from blogging.models import Content
from blogging.rest.serializers import ContentSerializer

from django.http import Http404


class ContentView(viewsets.ViewSet):
    queryset = Content.objects.all().order_by('-create_data')
    
    def list(self, request, format=None):
        print('In LIST')
        queryset = Content.objects.all().order_by('-create_date')
        serializer = ContentSerializer(queryset, 
                                       many=True, 
                                       context={'request':request})
        return Response(serializer.data)
    
    def create(self, request, format=None):
        print('In Create')
        serializer = ContentSerializer(data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return Content.objects.get(pk = pk)
        except Content.DoesNotExist:
            raise Http404
        
    def retrieve(self, request, pk, format=None):
        print('In Retrieve')
        obj = self.get_object(pk)
        serializer = ContentSerializer(instance=obj, 
                                       context={'request':request})
        return Response(serializer.data)
        
    def update(self, request, pk, format=None):
        print('In Update')
        obj = self.get_object(pk)
        serializer = ContentSerializer(instance=obj, data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk, format=None):
        print('In Partial Update')
        obj = self.get_object(pk)
        serializer = ContentSerializer(instance=obj, data=request.data, 
                                       context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk, format=None):
        print('In Destroy')
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)