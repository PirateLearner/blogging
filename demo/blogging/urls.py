'''
Created on 14-Mar-2018

@author: anshul
'''
from django.urls import path, re_path 

from . import views

app_name="blogging"

urlpatterns = [
    path('', views.index, name='index'),
    path('manage/', views.manage, name='manage'),
    path('<int:blog_id>/', views.detail, name='detail'),
    re_path(r'^edit/(?:(?P<blog_id>\d+)/)?$', 
            views.EditView.as_view(), 
            name="edit"),
    ]