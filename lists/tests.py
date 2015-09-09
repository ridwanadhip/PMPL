from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from lists.views import home_page

# Create your tests here.
# class SmokeTest(TestCase):
# 	def test_bad_maths(self):
# 		self.assertEqual(1+1, 3)

class HomePageTest(TestCase):
	def test_url_resolvers(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)

	def test_home_page(self):
		request = HttpRequest()
		response = home_page(request)
		self.assertTrue(response.content.startswith(b'<html>'))
		self.assertIn(b'<title>To-Do lists</title>', response.content)
		self.assertTrue(response.content.endswith(b'</html>\n'))
