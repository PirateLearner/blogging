'''
Created on 12-Mar-2018

@author: craft
'''
from django.test import TestCase

from blogging import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     "test creation."
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
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     "test creation."
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
                                                data = "We are entering some"+
                                                     "test data into this to"+
                                                     "test creation."
                                                )
        from_db = models.Content.objects.get(id=obj.id)
        from_db.delete()
        
        self.assertRaises(models.Content.DoesNotExist, 
                          models.Content.objects.get, id=obj.id)
        
    def test_create_multiple(self):
        obj_1 = models.Content.objects.create(author=self.user,
                                              title="Test Post",
                                              data = "We are entering some"+
                                                "test data into this to"+
                                                "test creation."
                                        )
        obj_2 = models.Content.objects.create(author=self.user,
                                              title="Another",
                                              data = "Some more data to test"+
                                                     "out multiple creations."
                                                )
        
        db_1 = models.Content.objects.get(id=obj_1.id)
        db_2 = models.Content.objects.get(id=obj_2.id)
        self.assertEqual(obj_1, db_1, "Instances are not equal")
        self.assertEqual(obj_2, db_2, "Instances are not equal")
        self.assertNotEqual(db_1, db_2, "Datas must not be the same")
        self.assertNotEqual(db_1.title, db_2.title, "Datas must not be the same")
        
    def test_fetch_multiple(self):
        #We might need to break this into multiple tests so that we are 
        # testing only one thing in one test.
        
        query_set = models.Content.objects.all()
        #Cannot compare with []. Returned is a Queryset object. Compare lengths.
        self.assertEqual(len(query_set), 0, "Non-Empty Query Set returned.")
        obj_1 = models.Content.objects.create(author=self.user,
                                              title="Test Post",
                                              data = "We are entering some"+
                                                "test data into this to"+
                                                "test creation."
                                        )
        obj_2 = models.Content.objects.create(author=self.user,
                                              title="Another",
                                              data = "Some more data to test"+
                                                     "out multiple creations."
                                                )
        obj_3 = models.Content(author=self.user,
                                              title="Another",
                                              data = "Some more data to test"+
                                                      "out multiple creations."
                                                )
        test_set = [obj_1, obj_2]
        query_set = models.Content.objects.all()
        self.assertNotIn(obj_3, 
                         query_set, 
                         "Object was not saved but found in DB")
        
        for blog in test_set:
            self.assertIn(blog, 
                          query_set, 
                          "Article created but not found in query_set")
        
    
    def test_content_deletion_on_user_delete(self):
        models.Content.objects.create(author=self.user,
                                              title="Test Post",
                                              data = "We are entering some"+
                                                "test data into this to"+
                                                "test creation."
                                        )
        models.Content.objects.create(author=self.user,
                                              title="Another",
                                              data = "Some more data to test"+
                                                     "out multiple creations."
                                                )
        self.user.delete()
        
        query_set = models.Content.objects.all()
        self.assertEqual(len(query_set), 
                         0, 
                         "Non-empty queryset returned \
                         even after deleting author")

    def test_create_content_without_title_or_content(self):
        obj = models.Content()
        obj.author = self.user
        
        #Ideally, at least one of them should be specified.
        self.assertRaises(ValidationError, obj.save, None)

    def test_create_content_without_title(self):
        obj = models.Content()
        obj.author = self.user
        obj.data = "We are entering some test data into this to test creation."
        
        obj.save()        
        #Ideally, at least one of them should be specified.
        self.assertEqual(obj.title, 
                         "We are entering some test data into this to", 
                         "Title is not as expected")
        
        db = models.Content.objects.get(id = obj.id)
        self.assertEqual(db.title, 
                         "We are entering some test data into this to", 
                         "Title is not as expected")

    def test_create_content_without_title_and_less_data(self):
        obj = models.Content()
        obj.author = self.user
        obj.data = "We are ."
        
        obj.save()        
        #Ideally, at least one of them should be specified.
        self.assertEqual(obj.title, 
                         "We are .", 
                         "Title is not as expected")
        
        db = models.Content.objects.get(id = obj.id)
        self.assertEqual(db.title, 
                         "We are .", 
                         "Title is not as expected")
        
class PolicyModel(BaseTest):
    def _create_post(self, title, data):
        return models.Content.objects.create(title=title, 
                                             data=data, 
                                             author=self.user)
        
    def test_policy_create(self):
        obj = self._create_post(title='Post 1', data='Some data')
        policy_obj = models.Policy(entry=obj, policy = models.Policy.PUBLISH)
        policy_obj.save()
        
        fetch_obj = models.Policy.objects.get(id=obj.id)
        self.assertEqual(policy_obj, fetch_obj, "Objects are not the same")
        
    def test_policy_with_publish_date(self):
        from django.utils import timezone
        obj = []
        obj.append(self._create_post(title='Post 1', data='Some data'))
        
        for entry in obj:
            policy_obj = models.Policy(entry=entry, 
                                       policy = models.Policy.PUBLISH,
                                       start=timezone.now())
            policy_obj.save()

        qs = models.Content.objects.get_published()
        returned_objs = []
        for entry in qs:
            returned_objs.append(entry)
        
        for entry in obj:
            self.assertIn(entry, returned_objs, "{o} not found".format(o=entry))