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
from blogging.factory import CreateTemplate

class BaseTest(APITestCase):
    def setUp(self):
        APITestCase.setUp(self)
        self.user = User.objects.create_superuser(username="Tester", 
                                             email="tester@testing.com", 
                                             password="testing123",
                                             )
        self.password = 'testing123'
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

    def test_get_empty_content_list_all_unpublished(self):
        obj = models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     " test creation."
                                                )
        Policy.objects.create(entry=obj, 
                              policy=Policy.PUBLISH, 
                              start=None)
        request = self.factory.get('/rest/content/')
        view = ContentView.as_view({'get': 'list'})
        
        response = view(request)
        
        self.assertEqual(response.status_code, 
                         status.HTTP_200_OK, 
                         "Status code must be 200,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        #print(json.loads(response.content))
        self.assertEqual(json.loads(response.content), 
                            [], 
                            "Non Empty response returned")
        
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
    
    def test_get_author_filter_1(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        
        obj = models.Content.objects.create(author=user,
                                                title="Test Post",
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     " test creation."
                                                )
        Policy.objects.create(entry=obj, 
                              policy=Policy.PUBLISH, 
                              start=timezone.now())

        
        request = self.factory.get('/rest/content/?author=tester2')
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


    def test_get_author_filter_2(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        
        obj = models.Content.objects.create(author=user,
                                            title="Test Post",
                                            data = "We are entering some"+
                                                   "test data into this to"+
                                                   " test creation."
                                                )
        Policy.objects.create(entry=obj, 
                              policy=Policy.PUBLISH, 
                              start=timezone.now())
        
        request = self.factory.get('/rest/content/?author=Tester')
        view = ContentView.as_view({'get': 'list'})
        
        response = view(request)
        
        self.assertEqual(response.status_code, 
                         status.HTTP_200_OK, 
                         "Status code must be 200,"+
                         " but {a} was returned".format(a=response.status_code))
        response.render() #Must be called before anything happens
        #print(json.loads(response.content))
        self.assertEqual(json.loads(response.content), 
                            [], 
                            "Non Empty response returned")
                

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
    

from blogging.settings import blog_settings

if blog_settings.USE_TEMPLATES:
    from blogging.rest.serializers import TemplateSerializer
    from blogging.models import Template, TemplateMap
    import os
    
    class TestTemplates(BaseTest):
        
        def test_create_new_template(self):
            
            self.client.force_authenticate(user=self.user)
            
            name = 'Blogging'
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}}]
            
            response = self.client.post('/rest/content/template/', 
                                        {'name':name,
                                         'fields': json.dumps(layout),
                                         })
            
            response.render() #Must be called before anything happens
            self.assertContains(response,
                                text='OK',
                                count=0,
                                status_code=status.HTTP_201_CREATED)
            
            qs = Template.objects.all()
            
            self.assertEqual(qs.count(), 1, "Only one DB entry must exist")
            
            for obj in qs:
                self.assertEqual(obj.name, name, "Improper name saved in DB")
            
            os.remove(CreateTemplate.get_full_file_path(CreateTemplate.get_file_name(name)))
        
        def test_create_duplicate_template_fails(self):
            self.client.force_authenticate(user=self.user)
            
            name = 'Blogging'
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}}]
            
            response = self.client.post('/rest/content/template/', 
                                        {'name':name,
                                         'fields': json.dumps(layout),
                                         })
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                                 {'body' : {'type': 'TextField',
                                            'extra': None
                                            }
                                  }]
            
            response = self.client.post('/rest/content/template/', 
                                        {'name':'blogging',
                                         'fields': json.dumps(layout),
                                         })
            response.render() #Must be called before anything happens
            self.assertContains(response,
                                text='OK',
                                count=0,
                                status_code=status.HTTP_400_BAD_REQUEST)
            qs = Template.objects.all()
            
            self.assertEqual(qs.count(), 1, "Only one DB entry must exist")
            
            for obj in qs:
                self.assertEqual(obj.name, 
                                    name, "Improper name saved in DB")
                
            os.remove(CreateTemplate.get_full_file_path(
                                     CreateTemplate.get_file_name(name)))
            
        
        @skip("Testing")
        def test_create_entry_with_template(self):
            self.client.force_authenticate(user=self.user)
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                 'extra': None
                                 }
                       }]
            
            name = 'Blogging'
            self.client.post('/rest/content/template/', 
                                        {'name':name,
                                         'fields': json.dumps(layout),
                                         })
            module_name = 'blogging.custom.'+\
                                    CreateTemplate.get_file_name(name)
            
            #Created. Now load
            from importlib import import_module
            module = import_module(module_name)
            
            serializer_name = CreateTemplate.get_serializer_name(name)
            model_name = CreateTemplate.get_model_name(name)
            
            serializer = getattr(module, serializer_name)
            model = getattr(module, model_name)
            
            #Loaded, now try to create
            ser_obj = serializer(data = {'title': 'Test Post',
                                        'body': 'This is a test post!'})
            
            if ser_obj.is_valid():
                ser_obj.save(author=self.user)
            
            mod_obj = models.Content.objects.get(id=1)
            #print(json.loads(mod_obj.data))
            #mod_obj = model.objects.get(id=1)
            
            #os.remove(CreateTemplate.get_full_file_path(
            #                        CreateTemplate.get_file_name(name)))