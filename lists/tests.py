from django.test import TestCase
from django.core.urlresolvers import resolve
from lists.views import home_page

# Create your tests here.
# class SmokeTest(TestCase):
# 	def test_bad_maths(self):
# 		self.assertEqual(1+1, 3)


class HomePageTest(TestCase):
	def test_url_resolvers(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)
