'''
Created on 15-Mar-2018

@author: anshul
'''
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from django.contrib.auth.models import User
from .serializers import UserSerializer

class UsersView(viewsets.ModelViewSet):
    """
    Simple viewset to view or edit Content
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CurrentUserView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def list(self, request, format=None):
        user_obj = self.request.user
        serializer = UserSerializer(user_obj,
                                    context={'request':request})
        return Response(serializer.data)