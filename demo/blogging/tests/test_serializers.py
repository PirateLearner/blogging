'''
Created on 15-Mar-2018

@author: anshul
'''
from django.contrib.auth.models import User
from rest_framework.test import (APIRequestFactory, 
                                 force_authenticate, 
                                 APITestCase)

from blogging.rest.serializers import ContentSerializer
from blogging.rest.views import ContentView, ManageView
from blogging import models

from rest_framework.request import Request
from rest_framework import status
from unittest import skip
from blogging.models import Policy

class BaseTest(APITestCase):
    def setUp(self):
        APITestCase.setUp(self)
        self.user = User.objects.create_superuser(username="Tester", 
                                             email="tester@testing.com", 
                                             password="testing123",
                                             )
        
        self.factory = APIRequestFactory()
        print("In method", self._testMethodName)

    def tearDown(self):
        APITestCase.tearDown(self)

import json
class listAPITests(BaseTest):
    def test_get_empty_content_list(self):
        request = self.factory.get('/rest/content/')
        view = ContentView.as_view({'get': 'list'})
        
        response = view(request)
        self.assertEqual(response.status_code, 
                         status.HTTP_200_OK, 
                         "Status code must be 200,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        
        self.assertListEqual(json.loads(response.content), 
                             [], 
                             "Non-empty list returned")
    
    def test_get_non_empty_content_list(self):
        from django.utils import timezone
        obj = models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     " test creation."
                                                )
        Policy.objects.create(entry=obj, 
                              policy=Policy.PUBLISH, 
                              start=timezone.now())
        request = self.factory.get('/rest/content/')
        view = ContentView.as_view({'get': 'list'})
        
        response = view(request)
        
        self.assertEqual(response.status_code, 
                         status.HTTP_200_OK, 
                         "Status code must be 200,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        #print(json.loads(response.content))
        self.assertNotEqual(json.loads(response.content), 
                            [], 
                            "Empty response returned")
        
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
        self.assertEqual(ser.data['title'], 'Test Post', 'Titles are dissimilar')
        self.assertEqual(ser.data['data'], "We are entering some"+
                                           "test data into this to"+
                                           " test creation.", 
                                           'Content is dissimilar')
    
    def test_post_new_content_with_login_disallowed(self):
        request = self.factory.post('/rest/content/', 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     'author': '/rest/users/1/'})
        user = User.objects.get(username=self.user.username)
        #request.user = self.user
        force_authenticate(request, user=user)
        
        view = ContentView.as_view({'post': 'create'})
        self.assertRaises(AttributeError, view, request)

        
    def test_post_new_content_with_login_in_client_disallowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest/content/', 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     'author': '/rest/users/1/'})
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_unpublished_post_absent_in_public_list(self):
        obj = models.Content.objects.create(author=self.user,
                                            title="Test Post",
                                            data = "We are entering some"+
                                                 "test data into this to"+
                                                 " test creation."
                                            )
        Policy.objects.create(entry=obj, policy=Policy.PUBLISH)
        
        response = self.client.get('/rest/content/')
        response.render()
        self.assertEqual(json.loads(response.content), 
                         [], 
                         "Response should be empty")
        

class manageAPITests(BaseTest):
    #Nothing is allowed without login credentials
    def test_get_empty_content_list(self):
        request = self.factory.get('/rest/content/manage')
        view = ManageView.as_view({'get': 'list'})
        
        response = view(request)
        self.assertEqual(response.status_code, 
                         status.HTTP_403_FORBIDDEN, 
                         "Status code must be 403,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        
    
    def test_get_non_empty_content_list(self):
        models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     " test creation."
                                                )
        
        request = self.factory.get('/rest/content/manage')
        view = ManageView.as_view({'get': 'list'})
        
        response = view(request)
        self.assertEqual(response.status_code, 
                         status.HTTP_403_FORBIDDEN, 
                         "Status code must be 403,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        #print(response.content)
        
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
        self.assertEqual(ser.data['title'], 'Test Post', 'Titles are dissimilar')
        self.assertEqual(ser.data['data'], "We are entering some"+
                                           "test data into this to"+
                                           " test creation.", 
                                           'Content is dissimilar')

    def test_post_new_content_without_login(self):
        request = self.factory.post('/rest/content/manage/', 
                                    {'title':'Test Post',
                                     'data': 'Data in test post'})
        view = ManageView.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.assertContains(response,
                            'You do not have permission to perform this action.',
                            count=0,#Is not detected
                            status_code = status.HTTP_403_FORBIDDEN,
                            html=False)
    
    def test_post_new_content_with_login(self):
        request = self.factory.post('/rest/content/manage/', 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     'author': '/rest/users/1/'})
        user = User.objects.get(username=self.user.username)
        #request.user = self.user
        force_authenticate(request, user=user)
        
        view = ManageView.as_view({'post': 'create'})
        response = view(request)
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_201_CREATED)
        self.assertEqual(len(models.Content.objects.filter(title='Test Post')), 
                         1, 
                         "Post not found in DB")
        
    def test_post_new_content_with_login_in_client(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest/content/manage/', 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     'author': '/rest/users/1/'})
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_201_CREATED)

    def test_post_new_content_with_login_without_author(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest/content/manage/', 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     })
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_201_CREATED)

    def test_post_new_content_without_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest/content/manage/', 
                                    {'title':'Test Post',
                                     })
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_201_CREATED)

    def test_post_new_content_without_data_or_title(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest/content/manage/', 
                                    {})
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_400_BAD_REQUEST)

    def test_post_with_empty_title_and_emtpy_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest/content/manage/', 
                                    {'title': ' ',
                                     'data': ''})
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_400_BAD_REQUEST)
        
    def test_post_new_content_with_policy_no_pk(self):
        pass
    

class detailAPITests(BaseTest):
    def test_get_non_existing_object(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest/content/1/')
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_404_NOT_FOUND)

    def test_get_non_existing_object_manage(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest/content/manage/1/')
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_404_NOT_FOUND)
    
    def test_unpublished_url_gives_404(self):
        obj = models.Content.objects.create(author=self.user,
                                            title="Test Post",
                                            data = "We are entering some"+
                                                 "test data into this to"+
                                                 " test creation."
                                            )
        Policy.objects.create(entry=obj, policy=Policy.PUBLISH)
        response = self.client.get('/rest/content/{obj}/'.format(obj=obj.id))
        response.render()
        self.assertContains(response, 
                            text='Not found', 
                            count=1, 
                            status_code=status.HTTP_404_NOT_FOUND)

    def test_get_on_exsting_object_without_login(self):
        obj = models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        from django.utils import timezone
        models.Policy.objects.create(entry=obj, 
                                     policy = models.Policy.PUBLISH,
                                     start=timezone.now())
        
        response = self.client.get('/rest/content/1/')
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_200_OK)

        text = json.loads(response.content)
        self.assertEqual(text['title'],
                         'Test Post',
                         "Titles don't match")
        self.assertEqual(text['data'],
                         "We are entering some"+
                         "test data into this to"+
                         " test creation.",
                         "Titles don't match")
        
    def test_get_on_exsting_object_without_login_manage(self):
        models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        response = self.client.get('/rest/content/manage/1/')
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_403_FORBIDDEN)


    def test_get_on_exsting_object_with_login(self):
        obj = models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        
        from django.utils import timezone
        models.Policy.objects.create(entry=obj, 
                                     policy = models.Policy.PUBLISH,
                                     start=timezone.now())
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest/content/1/')
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_200_OK)

        text = json.loads(response.content)
        self.assertEqual(text['title'],
                         'Test Post',
                         "Titles don't match")
        self.assertEqual(text['data'],
                         "We are entering some"+
                         "test data into this to"+
                         " test creation.",
                         "Titles don't match")

    def test_get_on_exsting_object_with_login_manage(self):
        models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/rest/content/manage/1/')
        response.render() #Must be called before anything happens
        self.assertContains(response,
                            text='OK',
                            count=0,
                            status_code=status.HTTP_200_OK)

        text = json.loads(response.content)
        self.assertEqual(text['title'],
                         'Test Post',
                         "Titles don't match")
        self.assertEqual(text['data'],
                         "We are entering some"+
                         "test data into this to"+
                         " test creation.",
                         "Titles don't match")
        
    def test_edit_on_existing_object_without_login(self):
        obj = models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        response = self.client.put('/rest/content/manage/{cid}/'.format(cid=obj.id), 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     })
        self.assertContains(response, 
                            text='Permission denied', 
                            count=0, 
                            status_code=status.HTTP_403_FORBIDDEN)
        
    def test_post_on_existing_object_with_login(self):
        obj = models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/rest/content/manage/{cid}/'.format(cid=obj.id), 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     })
        self.assertContains(response, 
                            text='OK', 
                            count=0, 
                            status_code=status.HTTP_200_OK)

    def test_put_on_existing_object_with_login(self):
        obj = models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        self.client.force_authenticate(user=self.user)
        response = self.client.put('/rest/content/manage/{cid}/'.format(cid=obj.id), 
                                    {'title':'Test Post',
                                     'data': 'Data in test post',
                                     })
        self.assertContains(response, 
                            text='OK', 
                            count=0, 
                            status_code=status.HTTP_200_OK)

    def test_delete_existing_object_without_login(self):
        obj = models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        response = self.client.delete('/rest/content/manage/{cid}/'.format(cid=obj.id))
        self.assertContains(response, 
                            text='OK', 
                            count=0, 
                            status_code=status.HTTP_403_FORBIDDEN)

    def test_delete_existing_object_with_login(self):
        obj = models.Content.objects.create(author=self.user,
                                        title="Test Post",
                                        data = "We are entering some"+
                                             "test data into this to"+
                                             " test creation."
                                        )
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/rest/content/manage/{cid}/'.format(cid=obj.id))
        self.assertContains(response, 
                            text='OK', 
                            count=0, 
                            status_code=status.HTTP_204_NO_CONTENT)

    def test_edit_content_with_policy_no_pk(self):
        pass
    
    def test_edit_content_with_policy(self):
        pass
    
