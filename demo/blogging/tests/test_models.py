'''
Created on 12-Mar-2018

@author: craft
'''
from django.test import TestCase

from blogging import models
from django.contrib.auth.models import User

class BaseTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="tester",
                                           email="tester@testing.co",
                                           password="secret")
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)


class ContentModel(BaseTest):
    def test_create_content(self):
        obj = models.blogContent()
        obj.author = self.user
        obj.title = "Test Post"
        obj.data = "We are entering some test data into this to test creation."
        
        obj.save()
        
        from_db = models.blogContent.objects.get(title="Test Post")
        self.assertIsInstance(from_db, 
                              models.blogContent, 
                              "Fetched instance is not blogContent")
        self.assertEqual(from_db, obj, "Objects don't match")
        self.assertEqual(from_db.author, self.user, "Authors don't match")
        
    
    def test_edit_content(self):
        pass
    
    def test_delete_content(self):
        pass
    
    def test_create_multiple(self):
        pass
    
    def test_fetch_multiple(self):
        pass
    
    
