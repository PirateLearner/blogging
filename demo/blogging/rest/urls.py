'''
Created on 15-Mar-2018

@author: anshul
'''
from django.urls import path, include
from rest_framework import routers
from blogging.rest import views

router = routers.SimpleRouter()
router.register(r'content/manage', views.ManageView,
                                                basename='content/manage')
router.register(r'content/template', views.TemplateView,
                                                basename='content/template')
router.register(r'content', views.ContentView,  basename='content')


urlpatterns = [
    path(r'',
         include(router.urls), name="blogging"),
    ]