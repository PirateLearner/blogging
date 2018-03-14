'''
Created on 14-Mar-2018

@author: anshul
'''
from django.urls import path 

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:blog_id>/', views.detail, name='detail'),
    ]