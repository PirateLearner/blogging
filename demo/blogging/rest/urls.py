'''
Created on 15-Mar-2018

@author: anshul
'''
from django.urls import path, include
from rest_framework import routers
from blogging.rest import views

router = routers.SimpleRouter()
router.register(r'content/manage', views.ManageView, 
                                                base_name='content/manage')
router.register(r'content/template', views.TemplateView, 
                                                base_name='content/template')
router.register(r'content', views.ContentView,  base_name='content')


urlpatterns = [
    path(r'', 
         include(router.urls), name="blogging"),
    ]