from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.views import home_page
from lists.models import Item


class HomePageTest(TestCase):
	def test_url_resolvers(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)

	def test_home_page(self):
		request = HttpRequest()
		response = home_page(request)
		expected_html = render_to_string('index.html')
		self.assertEqual(response.content.decode(), expected_html)
		# self.assertTrue(response.content.startswith(b'<html>'))
		# self.assertIn(b'<title>To-Do lists</title>', response.content)
		# self.assertTrue(response.content.strip().endswith(b'</html>'))

	def test_post_request(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['item_text'] = 'A new list item'

		response = home_page(request)

		self.assertIn('A new list item', response.content.decode())
		expected_html = render_to_string(
			'index.html',
			{'new_item_text': 'A new list item'}
		)

		self.assertEqual(response.content.decode(), expected_html)


class ItemModelTest(TestCase):
	def test_items(self):
		first_item = Item()
		first_item.text = 'The first (ever) list item'
		first_item.save()

		second_item = Item()
		second_item.text = 'Item the second'
		second_item.save()

		saved_items = Item.objects.all()
		self.assertEqual(saved_items.count(), 2)

		first_saved_item = saved_items[0]
		second_saved_item = saved_items[1]
		self.assertEqual(first_saved_item.text, 'The first (ever) list item')
		self.assertEqual(second_saved_item.text, 'Item the second')
