"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import resolve

from django.conf import settings

from blogging import views, models
from blogging.utils import slugify_name

from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from unittest import skip

project_name = settings.PROJECT_DIR

class SimpleTest(TestCase):
    
    def setUp(self):
        #Use request factory to test views without behaving like a browser
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester",
                                             email="tester@testing.co",
                                             password="secret")
        TestCase.setUp(self)

class ModelTests(SimpleTest):
    '''
    Tests on Models directly.
    '''
    def test_model_content_layout_slugfield(self):
        content_type = models.Layout(content_type=u"Test Layout")
        self.assertIsInstance(content_type, models.Layout, "Not a Layout Instance")
        
        content_type.save()
        self.assertEqual(content_type.model_name, slugify_name(u"Test Layout"), "Slug Fields are not equal")
        
    def test_model_create_content_layout(self):
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        
        from_db = models.Layout.objects.get(content_type="Test Layout")
        self.assertIsInstance(from_db, models.Layout, "Did not find the layout")
        self.assertEqual(content_type.id, from_db.id, "Primary Keys are not same")
    
    def test_model_create_section(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section.save()
        
        from_db = models.Section.objects.get(title="New Section")
        self.assertIsInstance(from_db, models.Section, "Fetched instance is not of Section type")
        self.assertEqual(from_db.id, section.id, "Section IDs do not match")
    
    def test_model_edit_section(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section.save()
        
        from_db = models.Section.objects.get(title="New Section")
        from_db.data = "We've changed the data now"
        from_db.title = "New Section Title"
        
        from_db.save()
        
        self.assertRaises(models.Section.DoesNotExist, 
                          models.Section.objects.get,
                          title="New Section")
        
        from_db = models.Section.objects.get(title="New Section Title")
        self.assertEqual(from_db.title, "New Section Title")
        self.assertEqual(from_db.data, "We've changed the data now")
        
    def test_model_create_many_sections(self):
         #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section_1 = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section_1.save()
        #Create another
        section_2 = models.Section(title='New Section 2',
                                 parent=None,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_2.save()
        
        from_db_1 = models.Section.objects.get(title="New Section")
        self.assertIsInstance(from_db_1, models.Section, "Fetched instance is not of Section type")
        self.assertEqual(from_db_1.id, section_1.id, "Section IDs do not match")
        
        from_db_2 = models.Section.objects.get(title="New Section 2")
        self.assertIsInstance(from_db_2, models.Section, "Fetched instance is not of Section type")
        self.assertEqual(from_db_2.id, section_2.id, "Section IDs do not match")
        
        from_db = models.Section.objects.all()
        self.assertEqual(len(from_db), 2, "Length should be 2. {len} returned".format(len=len(from_db)))

        
    def test_model_create_section_hierarchy(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section_1 = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section_1.save()
        #Create another
        section_2 = models.Section(title='New Section 2',
                                 parent=section_1,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_2.save()
        
        from_db_1 = models.Section.objects.get(title="New Section")
        self.assertIsInstance(from_db_1, models.Section, "Fetched instance is not of Section type")
        self.assertEqual(from_db_1.id, section_1.id, "Section IDs do not match")
        
        from_db_2 = models.Section.objects.get(title="New Section 2")
        self.assertIsInstance(from_db_2, models.Section, "Fetched instance is not of Section type")
        self.assertEqual(from_db_2.id, section_2.id, "Section IDs do not match")
        
        self.assertEqual(from_db_2.parent, section_1, "Section 2 parent isn't saved as section 1.")

        
    def test_model_edit_section_parent(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section_1 = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section_1.save()
        #Create another
        section_2 = models.Section(title='New Section 2',
                                 parent=section_1,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_2.save()
        
        from_db_1 = models.Section.objects.get(title="New Section")
        
        from_db_2 = models.Section.objects.get(title="New Section 2")
        from_db_2.parent = None
        from_db_2.save()
        
        from_db_2 = models.Section.objects.get(title="New Section 2")
        self.assertEqual(from_db_2.parent, None, "Section 2 parent isn't updated to None")

    def test_model_edit_section_parent_circular(self):
        '''
        Check if setting a child as parent of its parent fails or not.
        '''
        import mptt
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section_1 = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section_1.save()
        #Create another
        section_2 = models.Section(title='New Section 2',
                                 parent=section_1,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_2.save()
        
        from_db_1 = models.Section.objects.get(title="New Section")
        from_db_1.parent = section_2
        self.assertRaises(mptt.exceptions.InvalidMove, from_db_1.save)

    def test_model_create_section_name_uniqueness_same_parent(self):
        import django
        # Section names must be unique across siblings, but different parents may have them repeated
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section_1 = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section_1.save()
        #Create another
        section_2 = models.Section(title='New Section 2',
                                 parent=section_1,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_2.save()
        
        #Create another
        section_3 = models.Section(title='New Section 2',
                                 parent=section_1,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        #Should have been django.core.exceptions.ValidationError, but isn't. Why?
        self.assertRaises(django.db.utils.IntegrityError, section_3.save)

    def test_model_create_section_name_uniqueness_different_parent(self):
        # Section names must be unique across siblings, but different parents may have them repeated
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section_1 = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section_1.save()
        #Create another
        section_2 = models.Section(title='New Section 2',
                                 parent=section_1,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_2.save()
        
        #Create another root section
        section_3 = models.Section(title='New Section 3',
                                 parent=None,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_3.save()
        #Create another
        section_4 = models.Section(title='New Section 2',
                                 parent=section_3,
                                 data="Another new section has some description about itself",
                                 content_type=content_type)
        section_4.save()
        
        self.assertNotEqual(section_2, section_4, "Sections must be dissimilar entries")

    def test_model_delete_section(self):
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        #Create a section
        section_1 = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section_1.save()
        from_db_1 = models.Section.objects.get(title="New Section")
        from_db_1.delete()
        
        self.assertRaises(models.Section.DoesNotExist, 
                          models.Section.objects.get, title="New Section")

    
    def test_model_create_content(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        
        #Create a section
        section = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section.save()
        
        content = models.Content(title="New content",
                                 author_id=self.user,
                                 data="Some random content written by a whimsical tester",
                                 published_flag=False,
                                 special_flag=False,
                                 section=section,
                                 content_type=content_type)
        content.save()
        
        from_db = models.Content.objects.get(title="New content")
        self.assertIsInstance(from_db, models.Content, "Fetched instance is not of Content type")
        self.assertEqual(from_db.id, content.id, "Content IDs do not match")
        self.assertEqual(from_db.section, section, "Sections do not match")
        self.assertEqual(from_db.content_type, content_type, "Content types are different")

    def test_model_edit_content(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        
        #Create a section
        section = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section.save()
        
        content = models.Content(title="New content",
                                 author_id=self.user,
                                 data="Some random content written by a whimsical tester",
                                 published_flag=False,
                                 special_flag=False,
                                 section=section,
                                 content_type=content_type)
        content.save()
        
        from_db = models.Content.objects.get(title="New content")
        from_db.data="Now, new data has been written here"
        from_db.save()
        
        from_db = models.Content.objects.get(title="New content")
        self.assertEqual(from_db.id, content.id, "Content IDs do not match")
        self.assertEqual(from_db.section, section, "Sections do not match")
        self.assertEqual(from_db.content_type, content_type, "Content types are different")
        self.assertEqual(from_db.data, "Now, new data has been written here", "Edited data not saved")
    
    def test_model_delete_content(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        
        #Create a section
        section = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section.save()
        
        content = models.Content(title="New content",
                                 author_id=self.user,
                                 data="Some random content written by a whimsical tester",
                                 published_flag=False,
                                 special_flag=False,
                                 section=section,
                                 content_type=content_type)
        content.save()
        
        from_db = models.Content.objects.get(title="New content")
        from_db.delete()
        
        self.assertRaises(models.Content.DoesNotExist, 
                          models.Content.objects.get, title="New content")
    
    def test_model_delete_section_with_content(self):
        #Create a layout
        content_type = models.Layout(content_type=u"Test Layout")
        content_type.save()
        
        #Create a section
        section = models.Section(title='New Section',
                                 parent=None,
                                 data="A new section has some description about itself",
                                 content_type=content_type)
        section.save()
        
        content = models.Content(title="New content",
                                 author_id=self.user,
                                 data="Some random content written by a whimsical tester",
                                 published_flag=False,
                                 special_flag=False,
                                 section=section,
                                 content_type=content_type)
        content.save()
        
        section.delete()
        
        from_db = models.Content.objects.get(title="New content")
        self.assertEqual(from_db.section, None, "Parent Section must be NULL now")

class ViewTests(SimpleTest):
    '''
    Tests on Views.
    '''
    def test_base_url(self):
        '''
        User enters / and sees a bucket list of all top level 
        categories that we've made so far on the page
        '''
        found = resolve("/")
        self.assertEqual(found.func, 
                         views.teaser, 
                         "Could not find the view")
    
    def test_create_layout(self):
        '''
        Before any section or content is created from a view, a layout 
        must be created.
        
        While in the package, two default formats will be prepackaged:
        - Article
        - Section
        Creating Content will have the article format by default.
        Creating Sections will have the Section format by default. 
        '''
        found = resolve("/content-type/")
        self.assertEqual(found.func, 
                         views.content_type, 
                         "Could not find the view")
        
    def test_view_get_section_list(self):
        pass
    
    def test_view_get_section_detail(self):
        pass
    
    def test_view_get_content_list_all(self):
        pass
    
    def test_view_get_content_by_section(self):
        pass
    
    def test_view_get_content_by_parent_section(self):
        pass
    
    def test_view_get_content_layout(self):
        pass
    
    def test_view_content_type_create(self):
        pass
    
    def test_view_content_type_delete(self):
        pass
    
    def test_view_content_type_edit(self):
        pass
    
    def test_view_section_create(self):
        pass
    
    def test_view_section_edit(self):
        pass
    
    def test_view_section_delete(self):
        pass
    
    def test_view_content_create(self):
        pass
    
    def test_view_content_edit(self):
        pass
    
    def test_view_content_publish(self):
        pass
    
    def test_view_content_unpublish(self):
        pass
    
    def test_view_content_delete(self):
        pass
    
    def test_view_content_section_migration_on_section_delete(self):
        pass
    