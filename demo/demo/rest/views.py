'''
Created on 15-Mar-2018

@author: anshul
'''
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer

class UsersView(viewsets.ModelViewSet):
    """
    Simple viewset to view or edit Content
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer