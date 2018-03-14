'''
Created on 14-Mar-2018

@author: anshul
'''
from django.test import TestCase

from blogging import views, models
from django.contrib.auth.models import User

from django.test.client import RequestFactory, Client

from django.urls import resolve


class BaseTest(TestCase):
    def _create_post(self, title, data):
        models.Content.objects.create(title=title, data=data, author=self.user)
        
    def setUp(self):
        #Use request factory to test views without behaving like a browser
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester",
                                           email="tester@testing.co",
                                           password="secret")
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

from django.http import HttpRequest
class IndexView(BaseTest):
    def test_resolve_index_page(self):
        found = resolve("/blogging/")
        self.assertEqual(found.func, views.index, "Could not find view")

    def test_no_content_message_returned(self):
        request = HttpRequest()
        response = views.index(request)
        self.assertContains(response=response, 
                            text="Hi, no posts have been created.", 
                            count=1,
                            status_code=200)
        
    def test__client_no_content_message_returned(self):
        c = Client()
        response = c.get('/blogging/')
        self.assertContains(response=response, 
                            text="Hi, no posts have been created.", 
                            count=1,
                            status_code=200)
        

class DetailView(BaseTest):
    def test_resolve_detail_blog_page(self):
        found = resolve("/blogging/1/")
        self.assertEqual(found.func, views.detail, "Could not find view")
        
    def test_get_invalid_blog_id(self):
        request = HttpRequest()
        response = views.detail(request, blog_id=1)
        self.assertContains(response=response, 
                            text="Post does not exist", 
                            count=1,
                            status_code=404)