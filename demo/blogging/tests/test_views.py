'''
Created on 14-Mar-2018

@author: anshul
'''
from django.test import TestCase

from blogging import views, models
from django.contrib.auth.models import User

from django.test.client import RequestFactory, Client

from django.urls import resolve

from unittest import skip
from django.shortcuts import render

class BaseTest(TestCase):
    def _create_post(self, title, data):
        return models.Content.objects.create(title=title, 
                                             data=data, 
                                             author=self.user)
        
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
                            text="No posts have been created yet. Start writing!", 
                            count=1,
                            status_code=200)
        
    def test_client_no_content_message_returned(self):
        c = Client()
        response = c.get('/blogging/')
        self.assertContains(response=response, 
                            text="No posts have been created yet. Start writing!", 
                            count=1,
                            status_code=200)

    def test_get_non_empty_content_list(self):
        self._create_post(title="Post 1", data="This is post number 1")
        self._create_post(title="Post 2", data="This is post number 2")
        request = HttpRequest()
        response = views.index(request)
        
        self.assertContains(response=response, 
                            text="Post 1", 
                            count=1,
                            status_code=200)
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)

class DetailView(BaseTest):
    def test_resolve_detail_blog_page(self):
        found = resolve("/blogging/1/")
        self.assertEqual(found.func, views.detail, "Could not find view")
        
    def test_get_invalid_blog_id(self):
        from django.http import Http404
        request = HttpRequest()
        self.assertRaises(Http404, views.detail, request, blog_id=1)
        
    def test_get_valid_detail_page(self):
        obj = self._create_post(title="Post 1", data="This is post number 1")
#         html="<div>"+\
#              "<h1>Post 1</h1>"+\
#              "<div><span>Created on "+ obj.create_date.strftime("%B %d, %Y, %-H:%M %p")+\
#              " by "+ obj.author.username.title() +"</span></div>"+\
#              "<p>This is post number 1</p></div>"
        request = HttpRequest()
        response = views.detail(request, blog_id=1)
        self.assertContains(response=response, 
                            text="This is post number 1",
                            #text= html, 
                            count=1, 
                            status_code=200, 
                            html=True)

class EditView(BaseTest):
    def test_resolve_edit_page(self):
        found = resolve('/blogging/edit/')
        self.assertEqual(found.func.__name__, 
                         views.EditView.as_view().__name__, 
                         "The views are dissimilar")
    
    def test_template_used(self):
        c = Client()
        c.login(username='Tester', password='secret')
        response = c.get('/blogging/edit/')
        self.assertTemplateUsed(response, 'blogging/edit.html')
        
    def test_form_class(self):
        from blogging.forms import ContentForm
        c = Client()
        c.login(username='Tester', password='secret')
        response = c.get('/blogging/edit/')
        self.assertIsInstance(response.context['entry'], 
                              ContentForm, 
                              "The two forms are not the same types")
    
    
    @skip('Not working yet. Need selenium')
    def test_empty_form_returned(self):
        from django.template import RequestContext
        from django.template.loader import render_to_string
        from blogging.forms import ContentForm
         
        request = HttpRequest()
        request.method = 'GET'
        request.user = self.user
        view = views.EditView.as_view()
        response = view(request, blog_id=None)
        
        form = ContentForm(initial={'author': self.user})
        expected_html = render_to_string('blogging/edit.html', 
                                         context={'entry': form}, 
                                         request=request)
        