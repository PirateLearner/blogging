'''
Created on 14-Mar-2018

@author: anshul
'''
from django.urls import path, re_path 

from . import views
from blogging.settings import blog_settings

app_name="blogging"

urlpatterns = [
    path('', views.index, name='index'),
    path('manage/', views.manage_content, name='manage'),
    path('<int:blog_id>/', views.detail, name='detail'),
    re_path(r'^(?:(?P<blog_id>\d+)/)?edit/$', 
            views.EditView.as_view(), 
            name="edit"),
    ]

if blog_settings.USE_TEMPLATES:
    urlpatterns.insert(1, 
                   re_path(r'^template/(?:(?P<template_id>\d+)/)?edit/$', 
                           views.TemplateView.as_view(), 
                           name='template'))
    urlpatterns.insert(1, 
                   re_path(r'^template/$', 
                           views.manage_templates,
                           name='template/list'))