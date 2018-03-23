'''
Created on 15-Mar-2018

@author: anshul
'''
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from blogging.rest.serializers import ContentSerializer
from blogging.rest.views import ContentView
from blogging import models

from rest_framework.request import Request
from rest_framework import status
from unittest import skip

class BaseTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.user = User.objects.create_user(username="Tester", 
                                             email="tester@testing.com", 
                                             password="testing123")
        self.factory = APIRequestFactory()

    def tearDown(self):
        TestCase.tearDown(self)

import json
class getAPITests(BaseTest):
    def test_get_empty_content_list(self):
        request = self.factory.get('/rest/content/')
        view = ContentView.as_view({'get': 'list'})
        
        response = view(request)
        self.assertEqual(response.status_code, 
                         status.HTTP_200_OK, 
                         "Status code must be 200,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        
        self.assertListEqual(json.loads(response.content), [], "Non-empty list returned")
    
    def test_get_non_empty_content_list(self):
        obj = models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     " test creation."
                                                )
        
        request = self.factory.get('/rest/content/')
        view = ContentView.as_view({'get': 'list'})
        
        response = view(request)
        self.assertEqual(response.status_code, 
                         status.HTTP_200_OK, 
                         "Status code must be 200,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        #print(response.content)
        
    @skip('Skip')
    def test_get_list_from_serializer(self):
        obj = models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     " test creation."
                                                )
        
        request = self.factory.get('/')
        request_context = { 'request': Request(request),}
        
        ser = ContentSerializer(obj, context=request_context)
        print(ser.data)
