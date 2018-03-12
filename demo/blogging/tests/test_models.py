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
    def test_create_content_fetch_by_id(self):
        obj = models.Content()
        obj.author = self.user
        obj.title = "Test Post"
        obj.data = "We are entering some test data into this to test creation."
        
        obj.save()
        
        from_db = models.Content.objects.get(id=obj.id)
        self.assertIsInstance(from_db, 
                              models.Content, 
                              "Fetched instance is not Content")
        self.assertEqual(from_db, obj, "Objects don't match")
        self.assertEqual(from_db.author, self.user, "Authors don't match")
        
    def test_create_content_without_title_or_content(self):
        obj = models.Content()
        obj.author = self.user
        
        #Ideally, at least one of them should be specified.
        # TODO
        obj.save()
        #If only content is specified, then use first 7 words as title.
        
    def test_create_content_fetch_by_title(self):
        obj = models.Content()
        obj.author = self.user
        obj.title = "Test Post"
        obj.data = "We are entering some test data into this to test creation."
        
        obj.save()
        
        from_db = models.Content.objects.get(title="Test Post")
        self.assertIsInstance(from_db, 
                              models.Content, 
                              "Fetched instance is not Content")
        self.assertEqual(from_db, obj, "Objects don't match")
        self.assertEqual(from_db.author, self.user, "Authors don't match")
        
    def test_edit_content_title_field(self):
        obj = models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some \
                                                        test data into this to \
                                                        test creation."
                                                )
        from_db = models.Content.objects.get(id=obj.id)
        title = from_db.title
        from_db.title = "Changed Title"
        from_db.save()
        
        #Affirm we don't find it by previous title
        from_db = models.Content.objects.get(id=obj.id)
        self.assertNotEqual(title, from_db.title, "Titles must not be equal")
        self.assertEqual("Changed Title", 
                         from_db.title, 
                         "Changed title must be equal")

    def test_edit_content_data_field(self):
        obj = models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some \
                                                        test data into this to \
                                                        test creation."
                                                )
        from_db = models.Content.objects.get(id=obj.id)
        data = from_db.data
        from_db.data = "We have slightly modified the data"
        from_db.save()
        
        #Affirm we don't find it by previous title
        from_db = models.Content.objects.get(id=obj.id)
        self.assertNotEqual(data, 
                            from_db.data, 
                            "Data must not be equal to previous")
        self.assertEqual("We have slightly modified the data", 
                         from_db.data, 
                         "Changed data must be equal")
    
    
    def test_delete_content(self):
        obj = models.Content.objects.create(author=self.user,
                                                title="Test Post",
                                                data = "We are entering some \
                                                        test data into this to \
                                                        test creation."
                                                )
        from_db = models.Content.objects.get(id=obj.id)
        id = obj.id
        from_db.delete()
        
        self.assertRaises(models.Content.DoesNotExist, 
                          models.Content.objects.get, id=id)

    
    def test_create_multiple(self):
        pass
    
    def test_fetch_multiple(self):
        pass
    
    
