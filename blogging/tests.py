"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import resolve

from PirateLearner import settings
from blogging import views

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
    #User enters /C/ and sees a bucket list of all top level categories that we've made so far on the page
    def test_base_url(self):
        found = resolve("/C/")
        self.assertEqual(found.func, views.index, "Could not find the view")
