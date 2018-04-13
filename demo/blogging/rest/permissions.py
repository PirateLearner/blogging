'''
Created on 11-Apr-2018

@author: anshul
'''
from rest_framework.permissions import DjangoModelPermissions

class IsAdminOrAuthor(DjangoModelPermissions):
    
    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return (request.user == obj.author or request.user.is_staff)
