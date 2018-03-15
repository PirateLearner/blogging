'''
Created on 15-Mar-2018

@author: anshul
'''

from rest_framework import viewsets
from blogging.models import Content
from blogging.rest.serializers import ContentSerializer

class ContentView(viewsets.ModelViewSet):
    """
    Simple viewset to view or edit Content
    """
    queryset = Content.objects.all().order_by('-create_date')
    serializer_class = ContentSerializer